import asyncio
import fnmatch
import json
import logging
import mimetypes
import re
from datetime import datetime, timezone
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
from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.generic import KeyDictStore, KeySetStore
from telebot_components.utils.secrets import SecretStore

from telebot_constructor.app_models import (
    BotActionsHistory,
    BotInfo,
    BotTokenPayload,
    LoggedInUser,
    TgBotUser,
    TgBotUserUpdate,
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
from telebot_constructor.static import static_file_content
from telebot_constructor.telegram_files_downloader import (
    InmemoryCacheTelegramFilesDownloader,
    TelegramFilesDownloader,
)
from telebot_constructor.utils.pydantic import Language

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
        static_files_dir_override: Optional[Path] = None,
        telegram_files_downloader: Optional[TelegramFilesDownloader] = None,
    ) -> None:
        self.auth = auth
        self.secret_store = secret_store
        self.static_files_dir = static_files_dir_override or Path(__file__).parent / "static"
        logger.info(f"Will serve static frontend files from {self.static_files_dir.absolute()}")

        self.redis = redis
        self.telegram_files_downloader = telegram_files_downloader or InmemoryCacheTelegramFilesDownloader()

        # set during on of the setup/run methods to a concrete subclass
        self._runner: Optional[ConstructedBotRunner] = None

        # username -> {bot name -> bot config}
        self.bot_config_store = KeyDictStore[BotConfig](
            name="bot-configs",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=None,
            dumper=BotConfig.model_dump_json,
            loader=BotConfig.model_validate_json,
        )
        # username -> names of bots running at the moment
        self.running_bots_store = KeySetStore[str](
            name="bot-running",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=None,
        )
        # username -> names of bots running temporary configs at the moment
        self.temporary_running_bots_store = KeySetStore[str](
            name="temporary-bots-running",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=None,
        )
        # username -> names of bots and their actions history
        self.bot_history_store = KeyDictStore[BotActionsHistory](
            name="bot-history",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=None,
            dumper=BotActionsHistory.model_dump_json,
            loader=BotActionsHistory.model_validate_json,
        )

        self.group_chat_discovery_handler = GroupChatDiscoveryHandler(
            redis=redis,
            telegram_files_downloader=self.telegram_files_downloader,
        )

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
            raise web.HTTPBadRequest(reason="Name must consist of 3-32 alphanumeric characters, hyphens and dashes")

    def parse_bot_name(self, request: web.Request) -> str:
        name = request.match_info.get("bot_name")
        if name is None:
            raise web.HTTPNotFound()
        self._validate_name(name)
        return name

    async def parse_pydantic_model(self, request: web.Request, Model: Type[PydanticModelT]) -> PydanticModelT:
        try:
            return Model.model_validate(await request.json())
        except json.JSONDecodeError:
            raise web.HTTPBadRequest(reason="Request body must be valid JSON")
        except pydantic.ValidationError as e:
            raise web.HTTPBadRequest(text=e.json(include_context=False, include_url=False))
        except Exception as e:
            raise web.HTTPBadRequest(reason=str(e))

    def parse_secret_name(self, request: web.Request) -> str:
        name = request.match_info.get("secret_name")
        if name is None:
            raise web.HTTPNotFound()
        self._validate_name(name)
        return name

    async def load_bot_config(self, username: str, bot_name: str) -> BotConfig:
        config = await self.bot_config_store.get_subkey(username, bot_name)
        if config is None:
            raise web.HTTPNotFound(reason=f"No config found for bot name {bot_name!r}")
        return config

    async def load_bot_info(self, username: str, bot_name: str) -> BotInfo:
        bot_config = await self.bot_config_store.get_subkey(username, bot_name)
        bot_history = await self.bot_history_store.get_subkey(username, bot_name)
        if bot_config is None or bot_history is None:
            raise web.HTTPNotFound(reason=f"Not found info about bot name {bot_name!r}")
        else:
            bot_is_running = await self.running_bots_store.includes(username, bot_name)
            bot_info = BotInfo(
                display_name=bot_config.display_name,
                created_at=bot_history.created_at,
                last_updated_at=bot_history.last_updated_at,
                last_run_at=bot_history.last_run_at,
                is_running=bot_is_running,
            )
            return bot_info

    async def _make_raw_bot(self, username: str, bot_name: str) -> AsyncTeleBot:
        return await make_raw_bot(
            username,
            bot_config=await self.load_bot_config(username, bot_name),
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

    async def re_start_bot(
        self,
        username: str,
        bot_name: str,
        bot_config: BotConfig,
        is_temporary: bool = False,
    ) -> None:
        log_prefix = f"[{username}][{bot_name}]"
        logger.info(f"{log_prefix} (Re)starting bot")
        is_stopped = await self.runner.stop(username, bot_name)
        logger.info(f"{log_prefix} Stopped bot {is_stopped = }")
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
        if is_temporary:
            await self.temporary_running_bots_store.add(username, bot_name)
            await self.running_bots_store.remove(username, bot_name)
        else:
            await self.running_bots_store.add(username, bot_name)
            await self.temporary_running_bots_store.remove(username, bot_name)
            existing_bot_history = await self.bot_history_store.get_subkey(username, bot_name)
            if existing_bot_history:
                existing_bot_history.last_run_at = datetime.now(timezone.utc)
                await self.bot_history_store.set_subkey(key=username, subkey=bot_name, value=existing_bot_history)

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
        async def upsert_bot_config(request: web.Request) -> web.Response:
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
            existing_bot_config = await self.bot_config_store.get_subkey(username, bot_name)
            bot_config = await self.parse_pydantic_model(request, BotConfig)
            await self.bot_config_store.set_subkey(username, bot_name, bot_config)
            if bot_name in await self.running_bots_store.all(username):
                logger.info(f"Updated bot {bot_name} is running, restarting it")
                await self.re_start_bot(username, bot_name, bot_config)

            if existing_bot_config is None:
                new_bot_history = BotActionsHistory(
                    created_at=datetime.now(timezone.utc),
                    last_updated_at=datetime.now(timezone.utc),
                    last_run_at=None,
                    deleted_at=None,
                )
                await self.bot_history_store.set_subkey(key=username, subkey=bot_name, value=new_bot_history)

                return web.json_response(text=bot_config.model_dump_json(), status=201)
            else:
                existing_bot_history = await self.bot_history_store.get_subkey(username, bot_name)
                if existing_bot_history:
                    existing_bot_history.last_updated_at = datetime.now(timezone.utc)
                    await self.bot_history_store.set_subkey(key=username, subkey=bot_name, value=existing_bot_history)

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
            config = await self.load_bot_config(username, bot_name)
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
            config = await self.load_bot_config(username, bot_name)
            await self.runner.stop(username, bot_name)
            await self.running_bots_store.remove(username, bot_name)
            await self.bot_config_store.remove_subkey(username, bot_name)
            await self.secret_store.remove_secret(config.token_secret_name, owner_id=username)
            existing_bot_history = await self.bot_history_store.get_subkey(username, bot_name)
            if existing_bot_history:
                existing_bot_history.deleted_at = datetime.now(timezone.utc)
                await self.bot_history_store.set_subkey(key=username, subkey=bot_name, value=existing_bot_history)

            return web.json_response(text=config.model_dump_json())

        @routes.get("/api/config")
        async def list_bot_configs(request: web.Request) -> web.Response:
            """
            ---
            description: List all bot configs
            produces:
            - application/json
            responses:
                "200":
                    description: Bot name -> bot config mapping
            """
            username = await self.authenticate(request)
            bot_configs = await self.bot_config_store.load(username)
            return web.json_response(
                data={name: config.model_dump(mode="json") for name, config in bot_configs.items()}
            )

        ##################################################################################
        # bot lifecycle control: start, stop, list running

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
            bot_config = await self.load_bot_config(username, bot_name)
            await self.re_start_bot(username, bot_name, bot_config)

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
            if await self.runner.stop(username=username, bot_name=bot_name):
                await self.running_bots_store.remove(username, bot_name)
                return web.Response(text="Bot stopped")
            else:
                return web.Response(text="Bot was not running")

        @routes.get("/api/running")
        async def list_running_bots(request: web.Request) -> web.Response:
            """
            ---
            description: List running bots
            produces:
            - application/json
            responses:
                "200":
                    description: List of running bots' names
            """
            username = await self.authenticate(request)
            running_bots = await self.running_bots_store.all(username)
            return web.json_response(data=sorted(running_bots))

        ##################################################################################
        # bot info: all stat, is_running, last_run_at, etc
        @routes.get("/api/bots/info/{bot_name}")
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
            bot_info = await self.load_bot_info(username, bot_name)

            return web.json_response(text=bot_info.model_dump_json())

        @routes.get("/api/bots/info")
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
            bot_histories = await self.bot_history_store.load(username)
            bot_infos: dict[str, BotInfo] = {}

            for name, bot_info in bot_histories.items():
                bot_config = await self.bot_config_store.get_subkey(username, name)
                if bot_config is not None:
                    bot_is_running = await self.running_bots_store.includes(username, name)
                    bot_infos[name] = BotInfo(
                        display_name=bot_config.display_name,
                        created_at=bot_info.created_at,
                        last_updated_at=bot_info.last_updated_at,
                        last_run_at=bot_info.last_run_at,
                        is_running=bot_is_running,
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
                otherwise a temporary bot is constructed.
            produces:
            - application/json
            responses:
                "200":
                    description: OK
            """
            username = await self.authenticate(request)
            bot_name = self.parse_bot_name(request)
            if not await self.running_bots_store.includes(username, bot_name):
                logger.info("Group discovery mode requested but bot is not running, starting a temporary one instead")
                await self.re_start_bot(
                    username,
                    bot_name,
                    bot_config=(await self.load_bot_config(username, bot_name)).for_temporary_bot(),
                    is_temporary=True,
                )
            await self.group_chat_discovery_handler.start_discovery(username, bot_name)
            return web.Response(text="Group discovery started")

        @routes.post("/api/stop-group-chat-discovery/{bot_name}")
        async def stop_discovering_group_chats(request: web.Request) -> web.Response:
            """
            ---
            description: Stop "group discovery" mode. If a temporary bot was constructed it is stopped.
            produces:
            - application/json
            responses:
                "200":
                    description: OK
            """
            username = await self.authenticate(request)
            bot_name = self.parse_bot_name(request)
            await self.group_chat_discovery_handler.stop_discovery(username, bot_name)
            if await self.temporary_running_bots_store.includes(username, bot_name):
                await self.runner.stop(username, bot_name)
                await self.temporary_running_bots_store.remove(username, bot_name)
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
            chats.sort(
                key=lambda c: c.id
            )  # this is probably not chronological or anything, but at least it's consistent...
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
        # static file routes
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
                data=[{"code": lang.code, "name": lang.name, "emoji": lang.emoji} for lang in Language.all().values()]
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
            return web.Response(
                body=static_file_content(Path(__file__).parent / "data/prefilled_messages.json"),
                content_type="application/json",
            )

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
        """Run all bots that are stored as running; used on startup"""

        async def _start_stored_bots() -> None:
            logger.info("Starting stored bots")
            usernames = await self.running_bots_store.list_keys()
            logger.info("Found %s usernames with bot running flags", len(usernames))
            for username in usernames:
                running_bots = await self.running_bots_store.all(username)
                logger.info(f"{username!r} has {len(running_bots)} running bots: {sorted(running_bots)}")
                temp_running_bots = await self.temporary_running_bots_store.all(username)
                if temp_running_bots:
                    logger.info(
                        f"{username!r} also has {len(temp_running_bots)} "
                        + f"temporary running bots: {sorted(temp_running_bots)}"
                    )
                    intersection = temp_running_bots.intersection(running_bots)
                    if intersection:
                        logger.error(
                            f"{username!r} has {len(intersection)} bots marked as both "
                            + "running and temporary, removing temporary flag"
                        )
                    for bot_name in intersection:
                        temp_running_bots.remove(bot_name)
                        await self.temporary_running_bots_store.remove(username, bot_name)

                all_bot_names = [(name, False) for name in running_bots] + [(name, True) for name in temp_running_bots]
                for bot_name, is_temporary in all_bot_names:
                    bot_name_full = f"{bot_name!r} (owned by {username!r}, {is_temporary = })"
                    with log_error(marker=f"Starting stored bot {bot_name_full}", logger_=logger):
                        logger.info(f"Loading bot config for {bot_name_full})")
                        bot_config = await self.bot_config_store.get_subkey(username, bot_name)
                        if bot_config is None:
                            logger.error(f"Bot {bot_name_full} is marked as running, but has no config")
                            await (
                                self.running_bots_store if not is_temporary else self.temporary_running_bots_store
                            ).remove(username, bot_name)
                            continue
                        if is_temporary:
                            bot_config = bot_config.for_temporary_bot()
                        bot_runner = await self._construct_bot(username, bot_name, bot_config)
                        await self.runner.start(username=username, bot_name=bot_name, bot_runner=bot_runner)
                        logger.info(f"Started {bot_name_full}")

        self._start_stored_bots_task = create_error_logging_task(_start_stored_bots(), name="start stored bots")

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
        """For standalone run"""
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
        logger.info(f"Setting up telebot constructor web app on webhook app with base URL {webhook_app.base_url!r}")
        self._runner = WebhookAppConstructedBotRunner(webhook_app)
        await self.setup()
        app = await self.create_constructor_web_app()
        app.on_cleanup.append(lambda _: self.cleanup())
        webhook_app.aiohttp_app.add_subapp(BASE_PATH, app)
