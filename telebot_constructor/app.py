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
from telebot_constructor.runners import (
    ConstructedBotRunner,
    PollingConstructedBotRunner,
    WebhookAppConstructedBotRunner,
)
from telebot_constructor.static import static_file_content

logger = logging.getLogger(__name__)


PydanticModelT = TypeVar("PydanticModelT", bound=pydantic.BaseModel)


class TelebotConstructorApp:
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

        # user id -> {bot name -> config}
        self.bot_config_store = KeyDictStore[BotConfig](
            name="bot-configs",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=None,
            dumper=BotConfig.model_dump_json,
            loader=BotConfig.model_validate_json,
        )
        self.running_bots_store = KeySetStore[str](
            name="bot-running",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=None,
        )

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

    async def re_start_bot(self, username: str, bot_name: str, bot_config: BotConfig) -> None:
        log_prefix = f"[{username}][{bot_name}]"
        logger.info(f"{log_prefix} (Re)starting bot")
        is_stopped = await self.runner.stop(username, bot_name)
        logger.info(f"{log_prefix} Stopped bot {is_stopped = }")
        try:
            bot_runner = await construct_bot(
                username=username,
                bot_name=bot_name,
                bot_config=bot_config,
                secret_store=self.secret_store,
                redis=self.redis,
            )
        except Exception as e:
            logger.info(f"{log_prefix} Error constructing bot", exc_info=True)
            raise web.HTTPBadRequest(reason=str(e))
        if not await self.runner.start(username=username, bot_name=bot_name, bot_runner=bot_runner):
            logger.info(f"{log_prefix} Bot failed to start")
            raise web.HTTPInternalServerError(reason="Failed to start bot")
        logger.info(f"{log_prefix} Bot started OK!")
        await self.running_bots_store.add(username, bot_name)

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
            _ = await self.authenticate(request)
            token_payload = await self.parse_pydantic_model(request, BotTokenPayload)
            try:
                await AsyncTeleBot(token=token_payload.token).get_me()
            except Exception as e:
                raise web.HTTPBadRequest(reason=f"Bot token validation failed ({e})")
            return web.Response()

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

    async def _start_stored_bots(self) -> None:
        """Ensure that all bots stored as running are indeed running; used mainly on startup"""
        usernames = await self.running_bots_store.list_keys()
        logger.info("Found %s usernames with bot running flags", len(usernames))
        for username in usernames:
            running_bots = await self.running_bots_store.all(username)
            logger.info("Username %s has %s running bots: %s", usernames, len(running_bots), running_bots)
            for bot_name in running_bots:
                bot_config = await self.bot_config_store.get_subkey(username, bot_name)
                if bot_config is None:
                    logger.error(f"Bot {bot_name!r} is in running bots store, but has no config")
                    await self.running_bots_store.remove(username, bot_name)
                    continue
                try:
                    bot_runner = await construct_bot(
                        username=username,
                        bot_name=bot_name,
                        bot_config=bot_config,
                        secret_store=self.secret_store,
                        redis=self.redis,
                    )
                    await self.runner.start(username=username, bot_name=bot_name, bot_runner=bot_runner)
                except Exception:
                    logger.exception(f"Error creating bot {bot_name} ({username = })")

    # public methods to run constructor in different scenarios

    async def run_polling(self, port: int) -> None:
        """For standalone run"""
        logger.info("Running telebot constructor w/ polling")
        self._runner = PollingConstructedBotRunner()
        await self._start_stored_bots()
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
            logger.debug("Cleanup completed")
            await aiohttp_runner.cleanup()

    async def setup_on_webhook_app(self, webhook_app: WebhookApp) -> None:
        self._runner = WebhookAppConstructedBotRunner(webhook_app)
        await self._start_stored_bots()
        app = await self.create_constructor_web_app()
        webhook_app.aiohttp_app.add_subapp(BASE_PATH, app)
