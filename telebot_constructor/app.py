import asyncio
import fnmatch
import json
import logging
import mimetypes
import re
from pathlib import Path
from typing import Optional, Type, TypeVar

import pydantic
import telebot.api
from aiohttp import web
from aiohttp_swagger import setup_swagger  # type: ignore
from telebot import AsyncTeleBot
from telebot.runner import BotRunner
from telebot.util import create_error_logging_task, log_error
from telebot.webhook import WebhookApp
from telebot_components.language import LanguageData
from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.utils.secrets import SecretStore

from telebot_constructor.app_models import (
    BotTokenPayload,
    LoggedInUser,
    SaveBotConfigVersionPayload,
    StartBotPayload,
    TgBotUser,
    TgBotUserUpdate,
    UpdateBotDisplayNamePayload,
)
from telebot_constructor.auth.auth import Auth
from telebot_constructor.bot_config import BotConfig
from telebot_constructor.build_time_config import BASE_PATH
from telebot_constructor.construct import BotFactory, construct_bot, make_raw_bot
from telebot_constructor.cors import setup_cors
from telebot_constructor.debug import setup_debugging
from telebot_constructor.group_chat_discovery import GroupChatDiscoveryHandler
from telebot_constructor.runners import (
    ConstructedBotRunner,
    PollingConstructedBotRunner,
    WebhookAppConstructedBotRunner,
)
from telebot_constructor.static import get_prefilled_messages, static_file_content
from telebot_constructor.store.store import (
    BotConfigVersionMetadata,
    BotVersion,
    TelebotConstructorStore,
)
from telebot_constructor.store.types import (
    BotDeletedEvent,
    BotEditedEvent,
    BotStartedEvent,
    BotStoppedEvent,
)
from telebot_constructor.telegram_files_downloader import (
    InmemoryCacheTelegramFilesDownloader,
    TelegramFilesDownloader,
)

logger = logging.getLogger(__name__)


PydanticModelT = TypeVar("PydanticModelT", bound=pydantic.BaseModel)


class TelebotConstructorApp:
    """
    Main application class, managing aiohttp app setup (routes, middlewares) and running bots (via bot runner)
    """

    STORE_PREFIX = "telebot-constructor"

    def __init__(
        self,
        redis: RedisInterface,
        auth: Auth,
        secret_store: SecretStore,
        static_files_dir: Path = Path(__file__).parent / "static",
        telegram_files_downloader: Optional[TelegramFilesDownloader] = None,
    ) -> None:
        self.auth = auth
        self.secret_store = secret_store
        self.static_files_dir = static_files_dir
        logger.info(f"Will serve static frontend files from {self.static_files_dir.absolute()}")
        self.redis = redis

        self.telegram_files_downloader = telegram_files_downloader or InmemoryCacheTelegramFilesDownloader()
        self.store = TelebotConstructorStore(redis)
        self.group_chat_discovery_handler = GroupChatDiscoveryHandler(
            redis=redis, telegram_files_downloader=self.telegram_files_downloader
        )

        # set during on of the setup/run methods to a concrete subclass
        self._runner: Optional[ConstructedBotRunner] = None
        self._bot_factory: BotFactory = AsyncTeleBot  # for overriding during tests

    @property
    def runner(self) -> ConstructedBotRunner:
        if self._runner is None:
            raise RuntimeError("Constructed bot runner was not initialized properly")
        return self._runner

    async def _authenticate_full(self, request: web.Request) -> LoggedInUser:
        try:
            logged_in_user = await self.auth.authenticate_request(request)
        except Exception:
            logger.exception("Error autorizing user")
            logged_in_user = None
        if logged_in_user is None:
            raise web.HTTPUnauthorized(reason="Authentication required")
        return logged_in_user

    async def authenticate(self, request: web.Request) -> str:
        logged_in_user = await self._authenticate_full(request)
        return logged_in_user.username

    VALID_NAME_RE = re.compile(r"^[0-9a-zA-Z\-_]{3,64}$")

    def _validate_name(self, name: str) -> None:
        if not self.VALID_NAME_RE.match(name):
            raise web.HTTPBadRequest(reason="Name must consist of 3-64 alphanumeric characters, hyphens and dashes")

    def parse_bot_name(self, request: web.Request) -> str:
        name = request.match_info.get("bot_name")
        if name is None:
            raise web.HTTPNotFound()
        self._validate_name(name)
        return name

    def parse_version_query_param(self, request: web.Request) -> Optional[int]:
        version_str = request.query.get("version")
        if version_str is None:
            return None
        try:
            return int(version_str)
        except Exception:
            raise web.HTTPBadRequest(reason="version query argument must be a valid integer")

    async def parse_pydantic_model(self, request: web.Request, Model: Type[PydanticModelT]) -> PydanticModelT:
        try:
            return Model.model_validate(await request.json())
        except json.JSONDecodeError:
            raise web.HTTPBadRequest(reason="Request body must be valid JSON")
        except pydantic.ValidationError as e:
            raise web.HTTPBadRequest(
                text=e.json(include_context=False, include_url=False),
                content_type="application/json",
            )
        except Exception as e:
            raise web.HTTPBadRequest(reason=str(e))

    def parse_secret_name(self, request: web.Request) -> str:
        name = request.match_info.get("secret_name")
        if name is None:
            raise web.HTTPNotFound()
        self._validate_name(name)
        return name

    async def load_bot_config(self, username: str, bot_name: str, version: BotVersion) -> BotConfig:
        config = await self.store.load_bot_config(username, bot_name, version)
        if config is None:
            raise web.HTTPNotFound(reason=f"Bot not found: {bot_name!r}")
        return config

    async def _make_raw_bot(self, username: str, bot_name: str) -> AsyncTeleBot:
        return await make_raw_bot(
            username,
            bot_config=await self.load_bot_config(username, bot_name, version=-1),
            secret_store=self.secret_store,
            _bot_factory=self._bot_factory,
        )

    async def _construct_bot(self, username: str, bot_name: str, bot_config: BotConfig) -> BotRunner:
        return await construct_bot(
            username=username,
            bot_name=bot_name,
            bot_config=bot_config,
            secret_store=self.secret_store,
            redis=self.redis,
            group_chat_discovery_handler=self.group_chat_discovery_handler,
            _bot_factory=self._bot_factory,
        )

    async def stop_bot(self, username: str, bot_name: str) -> bool:
        if await self.runner.stop(username, bot_name):
            logger.info(f"[{username}][{bot_name}] Stopped bot")
            await self.store.set_bot_not_running(username, bot_name)
            await self.store.save_event(username, bot_name, event=BotStoppedEvent(username=username, event="stopped"))
            return True
        else:
            logger.info(f"[{username}][{bot_name}] Attempted to stop a bot but it was not running")
            return False

    async def start_bot(
        self,
        username: str,
        bot_name: str,
        version: BotVersion,
    ) -> None:
        """Start a specific version of the bot; this method should be initiated by a user"""
        bot_config = await self.load_bot_config(username, bot_name, version)
        log_prefix = f"[{username}][{bot_name}]"
        logger.info(f"{log_prefix} (Re)starting bot")
        await self.stop_bot(username, bot_name)
        try:
            bot_runner = await self._construct_bot(
                username=username,
                bot_name=bot_name,
                bot_config=bot_config,
            )
        except Exception as e:
            logger.info(f"{log_prefix} Error constructing bot", exc_info=True)
            raise web.HTTPBadRequest(reason=str(e))
        if not await self.runner.start(username=username, bot_name=bot_name, bot_runner=bot_runner):
            logger.info(f"{log_prefix} Bot failed to start")
            raise web.HTTPInternalServerError(reason="Failed to start bot")
        logger.info(f"{log_prefix} Bot started OK!")
        await self.store.set_bot_running_version(username, bot_name, version=version)
        await self.store.save_event(
            username,
            bot_name,
            event=BotStartedEvent(
                username=username,
                event="started",
                version=version,
            ),
        )

    async def create_constructor_web_app(self) -> web.Application:
        app = web.Application()
        routes = web.RouteTableDef()

        ##################################################################################
        # secrets

        @routes.post("/api/secrets/{secret_name}")
        async def upsert_secret(request: web.Request) -> web.Response:
            """
            ---
            description: Create or update secret
            responses:
                "201":
                    description: Success
            """
            username = await self.authenticate(request)
            secret_name = self.parse_secret_name(request)
            secret_value = await request.text()
            if not secret_value:
                raise web.HTTPBadRequest(reason="Secret can't be empty")
            result = await self.secret_store.save_secret(
                secret_name=secret_name,
                secret_value=secret_value,
                owner_id=username,
                allow_update=True,
            )
            return web.Response(text=result.message, status=200 if result.is_saved else 400)

        @routes.delete("/api/secrets/{secret_name}")
        async def delete_secret(request: web.Request) -> web.Response:
            """
            ---
            description: Delete secret
            responses:
                "201":
                    description: Success
            """
            username = await self.authenticate(request)
            secret_name = self.parse_secret_name(request)
            if await self.secret_store.remove_secret(
                secret_name=secret_name,
                owner_id=username,
            ):
                return web.Response(text="Removed", status=200)
            else:
                return web.Response(text="Secret not found", status=404)

        @routes.get("/api/secrets")
        async def list_secret_names(request: web.Request) -> web.Response:
            """
            ---
            description: List available secret names
            produces:
            - application/json
            responses:
                "201":
                    description: List of string secret names
            """
            username = await self.authenticate(request)
            secret_names = await self.secret_store.list_secrets(owner_id=username)
            return web.json_response(data=secret_names)

        ##################################################################################
        # bot configs CRUD

        @routes.post("/api/config/{bot_name}")
        async def save_new_bot_config_version(request: web.Request) -> web.Response:
            """
            ---
            description: Create or update bot configuration
            produces:
            - application/json
            responses:
                "201":
                    description: New bot is created, config is echoed back
                "200":
                    description: Bot config is updated, the old version of config is returned
            """
            username = await self.authenticate(request)
            bot_name = self.parse_bot_name(request)
            existing_bot_config = await self.store.load_bot_config(username, bot_name)
            payload = await self.parse_pydantic_model(request, SaveBotConfigVersionPayload)
            await self.store.save_bot_config(
                username,
                bot_name,
                config=payload.config,
                meta=BotConfigVersionMetadata(message=payload.version_message),
            )

            new_bot_version_count = await self.store.bot_config_version_count(username, bot_name)
            new_version = new_bot_version_count - 1  # i.e. the last one
            await self.store.save_event(
                username,
                bot_name,
                event=BotEditedEvent(
                    username=username,
                    event="edited",
                    new_version=new_version,
                ),
            )

            if payload.display_name is not None:
                await self.store.save_bot_display_name(username, bot_name, payload.display_name)

            if payload.start:
                await self.start_bot(username, bot_name, version=new_version)

            if existing_bot_config is None:
                return web.json_response(text=payload.config.model_dump_json(), status=201)
            else:
                return web.json_response(text=existing_bot_config.model_dump_json())

        @routes.get("/api/config/{bot_name}")
        async def get_bot_config(request: web.Request) -> web.Response:
            """
            ---
            description: Get config for bot with a given name
            produces:
            - application/json
            responses:
                "200":
                    description: OK
                "404":
                    description: No config found
            """
            username = await self.authenticate(request)
            bot_name = self.parse_bot_name(request)
            version = self.parse_version_query_param(request)
            config = await self.load_bot_config(
                username,
                bot_name,
                version=version if version is not None else -1,
            )

            # HACK: on query apram flag - emulate legacy behaviour where display name was stored inside bot config
            # to be removed
            if "with_display_name" in request.query:
                config.display_name = await self.store.load_bot_display_name(username, bot_name)
            return web.json_response(text=config.model_dump_json())

        @routes.delete("/api/config/{bot_name}")
        async def remove_bot_config(request: web.Request) -> web.Response:
            """
            ---
            description: Delete bot config; if the bot was running, it is stopped
            produces:
            - application/json
            responses:
                "200":
                    description: Deleted bot config
            """
            username = await self.authenticate(request)
            bot_name = self.parse_bot_name(request)
            config = await self.load_bot_config(username, bot_name, version=-1)
            await self.stop_bot(username, bot_name)
            await self.store.remove_bot_config(username, bot_name)
            await self.secret_store.remove_secret(config.token_secret_name, owner_id=username)
            await self.store.save_event(
                username,
                bot_name,
                BotDeletedEvent(username=username, event="deleted"),
            )
            return web.json_response(text=config.model_dump_json())

        ##################################################################################
        # bot lifecycle control: start, stop

        @routes.post("/api/start/{bot_name}")
        async def start_bot(request: web.Request) -> web.Response:
            """
            ---
            description: Start bot
            produces:
            - text/plain
            responses:
                "201":
                    description: Bot started
                "200":
                    description: Bot is already running
            """
            username = await self.authenticate(request)
            bot_name = self.parse_bot_name(request)
            payload = await self.parse_pydantic_model(request, StartBotPayload)
            await self.start_bot(username, bot_name, version=payload.version)
            return web.Response(text="OK", status=201)

        @routes.post("/api/stop/{bot_name}")
        async def stop_bot(request: web.Request) -> web.Response:
            """
            ---
            description: Stop bot
            produces:
            - text/plain
            responses:
                "201":
                    description: Bot stopped
                "200":
                    description: Bot was not running
            """
            username = await self.authenticate(request)
            bot_name = self.parse_bot_name(request)
            if await self.stop_bot(username, bot_name):
                return web.Response(text="Bot stopped")
            else:
                return web.Response(text="Bot was not running")

        ##################################################################################
        # bot info methods: name, running status, history, etc

        @routes.put("/api/display-name/{bot_name}")
        async def update_bot_display_name(request: web.Request) -> web.Response:
            """
            ---
            description: Update bot's display name, i.e. the one used in constructor web UI.
            produces:
            - application/json
            responses:
                "200":
                    description: Name changed OK
                "404":
                    description: Bot name does not exist
            """
            username = await self.authenticate(request)
            bot_name = self.parse_bot_name(request)
            payload = await self.parse_pydantic_model(request, UpdateBotDisplayNamePayload)
            if not await self.store.is_bot_exists(username, bot_name):
                raise web.HTTPNotFound(reason="Bot id not found")
            if await self.store.save_bot_display_name(username, bot_name, payload.display_name):
                return web.Response()
            else:
                raise web.HTTPInternalServerError(reason="Failed to save bot display name")

        @routes.get("/api/info/{bot_name}")
        async def get_bot_info(request: web.Request) -> web.Response:
            """
            ---
            description: Get info for bot with a given name
            produces:
            - application/json
            responses:
                "200":
                    description: OK
                "404":
                    description: No config found
            """
            username = await self.authenticate(request)
            bot_name = self.parse_bot_name(request)
            info = await self.store.load_bot_info(username, bot_name)
            if info is None:
                raise web.HTTPNotFound(reason="Bot id not found")
            else:
                return web.json_response(text=info.model_dump_json())

        @routes.get("/api/info")
        async def list_bot_infos(request: web.Request) -> web.Response:
            """
            ---
            description: List all bots with general info about running status, recent actions, etc
            produces:
            - application/json
            responses:
                "200":
                    description: List of all bots name and their statuses
            """
            username = await self.authenticate(request)
            bot_ids = await self.store.list_bot_ids(username)
            logger.info(f"Bots owned by {username}: {bot_ids}")
            maybe_bot_infos = {bot_id: await self.store.load_bot_info(username, bot_id) for bot_id in bot_ids}
            bot_infos = {bot_id: info for bot_id, info in maybe_bot_infos.items() if info is not None}
            if len(maybe_bot_infos) != len(bot_infos):
                missing_info_bot_ids = set(maybe_bot_infos.keys()).difference(bot_infos.keys())
                logger.error(
                    "Failed to construct bot infos for some of the user's bots, will ignore them: "
                    + f"{missing_info_bot_ids}"
                )
            return web.json_response(
                data={name: bot_info.model_dump(mode="json") for name, bot_info in bot_infos.items()}
            )

        ##################################################################################
        # validation endpoints

        @routes.post("/api/validate-token")
        async def validate_bot_token(request: web.Request) -> web.Response:
            """
            ---
            description: Validate Telegram bot token
            produces:
            - application/json
            responses:
                "200":
                    description: OK
                "400":
                    description: Invalid token (with forwarded Telegram bot API response)
            """
            _ = await self.authenticate(request)
            token_payload = await self.parse_pydantic_model(request, BotTokenPayload)
            try:
                await AsyncTeleBot(token=token_payload.token).get_me()
            except Exception as e:
                raise web.HTTPBadRequest(reason=f"Bot token validation failed ({e})")
            return web.Response(text="Token is valid")

        ##################################################################################
        # endpoints for syncing constructor state with telegram

        @routes.get("/api/bot-user/{bot_name}")
        async def get_bot_user(request: web.Request) -> web.Response:
            """
            ---
            description: Retrieve info about bot account (username, name, settings, ...)
            produces:
            - application/json
            responses:
                "200":
                    description: TgBotUser object
            """
            username = await self.authenticate(request)
            bot_name = self.parse_bot_name(request)
            bot = await self._make_raw_bot(username, bot_name)
            try:
                tg_bot_user = await TgBotUser.fetch(bot, telegram_files_downloader=self.telegram_files_downloader)
                return web.json_response(tg_bot_user.model_dump())
            except Exception:
                logger.exception("Unexpected error retrieving tg bot user info")
                raise web.HTTPInternalServerError(reason="Failed to retrieve bot user details")

        @routes.put("/api/bot-user/{bot_name}")
        async def update_bot_user(request: web.Request) -> web.Response:
            """
            ---
            description: Update bot info (name, description and short descrition)
            produces:
            - application/json
            responses:
                "200":
                    description: OK
            """
            username = await self.authenticate(request)
            bot_name = self.parse_bot_name(request)
            bot_user_update = await self.parse_pydantic_model(request, TgBotUserUpdate)
            if not bot_user_update.name:
                raise web.HTTPBadRequest(reason="Bot name can't be empty")
            bot = await self._make_raw_bot(username, bot_name)
            try:
                await bot_user_update.save(bot, telegram_files_downloader=self.telegram_files_downloader)
                return web.Response(reason="OK")
            except Exception:
                logger.exception("Error updating bot user info")
                raise web.HTTPInternalServerError(reason="Error updating bot detailed information")

        @routes.post("/api/start-group-chat-discovery/{bot_name}")
        async def start_discovering_group_chats(request: web.Request) -> web.Response:
            """
            ---
            description: |
                Start "group discovery" mode. For running bot it means just adding a few handlers,
                otherwise a stub bot is run.
            produces:
            - application/json
            responses:
                "200":
                    description: OK
            """
            username = await self.authenticate(request)
            bot_name = self.parse_bot_name(request)
            if not await self.store.is_bot_running(username, bot_name):
                logger.info("Group discovery mode requested but bot is not running, starting stub bot")
                await self.start_bot(username, bot_name, version="stub")
            await self.group_chat_discovery_handler.start_discovery(username, bot_name)
            return web.Response(text="Group discovery started")

        @routes.post("/api/stop-group-chat-discovery/{bot_name}")
        async def stop_discovering_group_chats(request: web.Request) -> web.Response:
            """
            ---
            description: Stop "group discovery" mode. If a stub bot was used it is stopped.
            produces:
            - application/json
            responses:
                "200":
                    description: OK
            """
            username = await self.authenticate(request)
            bot_name = self.parse_bot_name(request)
            await self.group_chat_discovery_handler.stop_discovery(username, bot_name)
            if await self.store.get_bot_running_version(username, bot_name) == "stub":
                logger.info("Group discovery mode stopped and bot stub was running, stopping it")
                await self.stop_bot(username, bot_name)
            return web.Response(text="Group discovery stopped")

        @routes.get("/api/available-group-chats/{bot_name}")
        async def get_available_group_chats(request: web.Request) -> web.Response:
            """
            ---
            description: Get discovered and validated chats currently available to the bot
            produces:
            - application/json
            responses:
                "200":
                    description: List of TgGroupChat objects
            """
            username = await self.authenticate(request)
            bot_name = self.parse_bot_name(request)
            chats = await self.group_chat_discovery_handler.validate_discovered_chats(
                username,
                bot_name,
                bot=await self._make_raw_bot(username, bot_name),
            )
            # this is probably not chronological or anything, but at least it's consistent...
            chats.sort(key=lambda c: c.id)
            return web.json_response(data=[chat.model_dump(mode="json") for chat in chats])

        @routes.get("/api/group-chat/{bot_name}")
        async def get_group_chat(request: web.Request) -> web.Response:
            """
            ---
            description: Retrieve info about a group chat available to bot
            produces:
            - application/json
            responses:
                "200":
                    description: TgGroupChat object
                "404":
                    description: Chat not found
            """
            username = await self.authenticate(request)
            bot_name = self.parse_bot_name(request)
            bot = await self._make_raw_bot(username, bot_name)
            # NOTE: numeric chat ids are not casted into ints because it doesn't matter for Telegram bot API
            group_chat_id = request.query.get("group_chat")
            if group_chat_id is None:
                raise web.HTTPBadRequest(reason="group_chat query param expected")
            chat = await self.group_chat_discovery_handler.get_group_chat(bot=bot, chat_id=group_chat_id)
            if chat is None:
                raise web.HTTPNotFound(reason="Chat does not exist or is not available to the bot")
            else:
                return web.json_response(data=chat.model_dump(mode="json"))

        ##################################################################################
        # static content routes

        @routes.get("/api/all-languages")
        async def all_languages(request: web.Request) -> web.Response:
            """
            ---
            description: List all available languages with code, name and emoji, if exists
            produces:
            - application/json
            responses:
                "200":
                    description: List of Language objects
            """
            await self.authenticate(request)
            return web.json_response(
                data=[
                    {
                        "code": lang.code,
                        "name": lang.name,
                        "emoji": lang.emoji,
                    }
                    for lang in LanguageData.all().values()
                ]
            )

        @routes.get("/api/prefilled-messages")
        async def prefilled_messages(request: web.Request) -> web.Response:
            """
            ---
            description: List all available languages with code, name and emoji, if exists
            produces:
            - application/json
            responses:
                "200":
                    description: List of Language objects
            """
            await self.authenticate(request)
            return web.Response(body=get_prefilled_messages(), content_type="application/json")

        @routes.get("/api/logged-in-user")
        async def get_logged_in_user(request: web.Request) -> web.Response:
            """
            ---
            description: Get logged in user with auth-specific details
            produces:
            - application/json
            responses:
                "200":
                    description: LoggedInUser object
            """
            user = await self._authenticate_full(request)
            return web.Response(
                body=user.model_dump_json(),
                content_type="application/json",
            )

        @routes.get("/")
        async def index(request: web.Request) -> web.Response:
            username = await self.auth.authenticate_request(request)
            if username is None:
                return await self.auth.unauthenticated_client_response(request, static_files_dir=self.static_files_dir)
            return web.Response(
                body=static_file_content(self.static_files_dir / "index.html"),
                content_type="text/html",
            )

        STATIC_FILE_GLOBS = ["assets/*", "favicon.ico"]

        @routes.get("/{path:(?!api/).*}")  # mathing all paths except those starting with /api prefix
        async def serve_static_file(request: web.Request) -> web.StreamResponse:
            static_file_path = request.match_info.get("path")
            if static_file_path is None:
                raise web.HTTPNotFound()
            if any(fnmatch.fnmatch(static_file_path, glob) for glob in STATIC_FILE_GLOBS):
                mime_type, _ = mimetypes.guess_type(static_file_path, strict=False)
                return web.Response(
                    body=static_file_content(self.static_files_dir / static_file_path),
                    content_type=mime_type,
                )
            else:
                # falling back to index page to support client-side routing
                return await index(request)

        ##################################################################################

        app.add_routes(routes)
        await self.auth.setup_routes(app)
        setup_swagger(app=app, swagger_url="/api/swagger")
        setup_cors(app)
        setup_debugging(app)
        return app

    def start_stored_bots_in_background(self) -> None:
        async def _start_stored_bots() -> None:
            logger.info("Starting stored bots...")
            count = 0
            async for username, bot_name, version in self.store.iter_running_bot_versions():
                count += 1
                bot_name_full = f"{bot_name!r} (owned by {username!r}, ver {version})"
                logger.debug(f"Starting {bot_name_full} (#{count})")
                with log_error(marker=f"Starting stored bot {bot_name_full}", logger_=logger):
                    bot_config = await self.store.load_bot_config(username, bot_name, version)
                    if bot_config is None:
                        logger.error(f"{bot_name_full} is running but has no config")
                        await self.store.set_bot_not_running(username, bot_name)
                        continue
                    bot_runner = await self._construct_bot(username, bot_name, bot_config)
                    if not await self.runner.start(username=username, bot_name=bot_name, bot_runner=bot_runner):
                        logger.error(f"{bot_name_full} failed to start")
            logger.info(f"Started {count} stored bots")

        self._start_stored_bots_task = create_error_logging_task(_start_stored_bots(), name="Start stored bots")

    async def setup(self) -> None:
        self.start_stored_bots_in_background()
        auth_bot_runner = await self.auth.setup_bot()
        if auth_bot_runner is not None:
            logger.info("Starting auth bot")
            await self.runner.start(username="internal", bot_name="auth-bot", bot_runner=auth_bot_runner)
        await self.telegram_files_downloader.setup()

    async def cleanup(self) -> None:
        logger.info("Cleanup started")
        await self.telegram_files_downloader.cleanup()
        await self.runner.cleanup()
        await telebot.api.session_manager.close_session()
        logger.info("Cleanup completed")

    # public methods to run constructor in different scenarios

    async def run_polling(self, port: int) -> None:
        """Standalone run, polling is used to get updates from Telegram API"""
        logger.info("Running telebot constructor w/ polling")
        self._runner = PollingConstructedBotRunner()
        await self.setup()
        aiohttp_app = await self.create_constructor_web_app()
        aiohttp_runner = web.AppRunner(aiohttp_app)
        await aiohttp_runner.setup()
        site = web.TCPSite(aiohttp_runner, "0.0.0.0", port)
        logger.info(f"Running server on {site.name}")
        try:
            await site.start()
            while True:
                await asyncio.sleep(3600)
        finally:
            await aiohttp_runner.cleanup()
            await self.cleanup()

    async def setup_on_webhook_app(self, webhook_app: WebhookApp) -> None:
        """Run constructor app as part of larger application, represented by a WebhookApp instance"""
        logger.info(f"Setting up telebot constructor web app on webhook app with base URL {webhook_app.base_url!r}")
        self._runner = WebhookAppConstructedBotRunner(webhook_app)
        await self.setup()
        app = await self.create_constructor_web_app()
        app.on_cleanup.append(lambda _: self.cleanup())
        webhook_app.aiohttp_app.add_subapp(BASE_PATH, app)
