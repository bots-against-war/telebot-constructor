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
from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.generic import KeyDictStore, KeySetStore
from telebot_components.utils.secrets import SecretStore

from telebot_constructor.app_models import BotTokenPayload
from telebot_constructor.auth import Auth
from telebot_constructor.bot_config import BotConfig
from telebot_constructor.build_time_config import BASE_PATH
from telebot_constructor.construct import construct_bot
from telebot_constructor.cors import setup_cors
from telebot_constructor.debug import setup_debugging
from telebot_constructor.group_chat_discovery import GroupChatDiscoveryHandler
from telebot_constructor.runners import (
    ConstructedBotRunner,
    PollingConstructedBotRunner,
    WebhookAppConstructedBotRunner,
)
from telebot_constructor.static import static_file_content

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
    ) -> None:
        self.auth = auth
        self.secret_store = secret_store
        self.static_files_dir = static_files_dir_override or Path(__file__).parent / "static"
        self._runner: Optional[ConstructedBotRunner] = None
        self.redis = redis
        logger.info(f"Will serve static frontend files from {self.static_files_dir.absolute()}")

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

        self.group_chat_discovery_handler = GroupChatDiscoveryHandler(redis=redis)

    @property
    def runner(self) -> ConstructedBotRunner:
        if self._runner is None:
            raise RuntimeError("Constructed bot runner was not initialized properly")
        return self._runner

    async def authenticate(self, request: web.Request) -> str:
        username = await self.auth.authenticate_request(request)
        if username is None:
            raise web.HTTPUnauthorized(reason="Authentication required")
        return username

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

    async def _construct_bot(self, username: str, bot_name: str, bot_config: BotConfig) -> BotRunner:
        return await construct_bot(
            username=username,
            bot_name=bot_name,
            bot_config=bot_config,
            secret_store=self.secret_store,
            redis=self.redis,
            group_chat_discovery_handler=self.group_chat_discovery_handler,
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

    async def create_constructor_web_app(self) -> web.Application:
        app = web.Application()
        routes = web.RouteTableDef()

        ##################################################################################
        # secrets C_UD

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
        async def upsert_new_bot_config(request: web.Request) -> web.Response:
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
                return web.json_response(text=bot_config.model_dump_json(), status=201)
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
            return web.Response()

        ##################################################################################
        # endpoints for syncing constructor state with telegram
        @routes.get("/api/bot-account/{bot_name}")
        async def get_bot_account(request: web.Request) -> web.Response:
            """
            ---
            description: Retrieve info about bot account (username, name, settings, ...)
            produces:
            - application/json
            responses:
                "200":
                    description: OK
            """
            username = await self.authenticate(request)
            bot_name = self.parse_bot_name(request)
            bot_runner = await self._construct_bot(
                username,
                bot_name,
                bot_config=BotConfig.for_temporary_bot(await self.load_bot_config(username, bot_name)),
            )
            await bot_runner.bot.get_me()
            # TODO call several other methods to get bot's description and stuff and pack it into our custom obj
            return web.Response()

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
                    bot_config=BotConfig.for_temporary_bot(real_config=await self.load_bot_config(username, bot_name)),
                    is_temporary=True,
                )
            await self.group_chat_discovery_handler.start_discovery(username, bot_name)
            return web.Response()

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
            return web.Response()

        @routes.get("/api/available-group-chats/{bot_name}")
        async def get_available_group_chats(request: web.Request) -> web.Response:
            """
            ---
            description: Get discovered and validated chats currently available to the bot
            produces:
            - application/json
            responses:
                "200":
                    description: OK
            """
            username = await self.authenticate(request)
            bot_name = self.parse_bot_name(request)
            bot_config = BotConfig.for_temporary_bot(await self.load_bot_config(username, bot_name))
            bot_runner = await self._construct_bot(username, bot_name, bot_config)
            chats = await self.group_chat_discovery_handler.validate_discovered_chats(
                username, bot_name, bot=bot_runner.bot
            )
            return web.json_response(data=[chat.model_dump(mode="json") for chat in chats])

        ##################################################################################
        # static file routes

        @routes.get("/")
        async def index(request: web.Request) -> web.Response:
            username = await self.auth.authenticate_request(request)
            if username is None:
                return await self.auth.unauthenticated_client_response(request, static_files_dir=self.static_files_dir)
            return web.Response(
                body=static_file_content(self.static_files_dir / "index.html"),
                content_type="text/html",
            )

        STATIC_FILE_GLOBS = ["assets/*"]

        @routes.get("/{tail:.+}")
        async def serve_static_file(request: web.Request) -> web.StreamResponse:
            static_file_path = request.match_info.get("tail")
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
        setup_swagger(app=app, swagger_url="/swagger")
        await self.auth.setup_routes(app)
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
                            bot_config = BotConfig.for_temporary_bot(bot_config)
                        bot_runner = await self._construct_bot(username, bot_name, bot_config)
                        await self.runner.start(username=username, bot_name=bot_name, bot_runner=bot_runner)
                        logger.info(f"Started {bot_name_full}")

        self._start_stored_bots_task = create_error_logging_task(_start_stored_bots(), name="start stored bots")

    # public methods to run constructor in different scenarios

    async def run_polling(self, port: int) -> None:
        """For standalone run"""
        logger.info("Running telebot constructor w/ polling")
        self._runner = PollingConstructedBotRunner()
        self.start_stored_bots_in_background()
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
            logger.info("Cleanup started")
            await self.runner.cleanup()
            await telebot.api.session_manager.close_session()
            await aiohttp_runner.cleanup()
            logger.info("Cleanup completed")

    async def setup_on_webhook_app(self, webhook_app: WebhookApp) -> None:
        logger.info(f"Setting up telebot constructor web app on webhook app with base URL {webhook_app.base_url!r}")
        self._runner = WebhookAppConstructedBotRunner(webhook_app)
        self.start_stored_bots_in_background()
        app = await self.create_constructor_web_app()
        webhook_app.aiohttp_app.add_subapp(BASE_PATH, app)
