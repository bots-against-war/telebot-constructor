import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Optional

import pydantic
import telebot.api
from aiohttp import web
from aiohttp_swagger import setup_swagger  # type: ignore
from telebot.webhook import WebhookApp
from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.generic import KeyDictStore, KeySetStore

from telebot_constructor.auth import Auth
from telebot_constructor.bot_config import BotConfig
from telebot_constructor.construct import construct_bot
from telebot_constructor.runners import (
    ConstructedBotRunner,
    PollingConstructedBotRunner,
    WebhookAppConstructedBotRunner,
)
from telebot_constructor.static import static_file_content

logger = logging.getLogger(__name__)


class TelebotConstructorApp:
    STORE_PREFIX = "telebot-constructor"
    URL_PREFIX = "/constructor"

    def __init__(self, redis: RedisInterface, auth: Auth, static_files_dir_override: Optional[Path] = None) -> None:
        self.auth = auth
        self.static_files_dir = static_files_dir_override or Path(__file__).parent / "static"
        self._runner: Optional[ConstructedBotRunner] = None
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

    VALID_BOT_NAME_RE = re.compile(r"^[0-9a-zA-Z\-_]{5,16}$")

    def parse_bot_name(self, request: web.Request) -> str:
        name = request.match_info.get("bot_name")
        if name is None:
            raise web.HTTPNotFound()
        if not self.VALID_BOT_NAME_RE.match(name):
            raise web.HTTPBadRequest(reason="Bot name must consist of 5-16 alphanumeric characters, hyphens and dashes")
        return name

    async def load_bot_config(self, username: str, bot_name: str) -> BotConfig:
        config = await self.bot_config_store.get_subkey(username, bot_name)
        if config is None:
            raise web.HTTPNotFound(reason=f"No config found for bot name {bot_name!r}")
        return config

    async def setup_routes(self, app: web.Application) -> None:
        routes = web.RouteTableDef()

        ##################################################################################
        # static file routes

        @routes.get(self.URL_PREFIX)
        async def index(request: web.Request) -> web.Response:
            username = await self.auth.authenticate_request(request)
            if username is None:
                return await self.auth.unauthenticated_client_response(request, static_files_dir=self.static_files_dir)
            return web.Response(
                body=static_file_content(self.static_files_dir / "index.html"),
                content_type="text/html",
            )

        ##################################################################################
        # bot configs CRUD

        @routes.post(self.URL_PREFIX + "/config/{bot_name}")
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
            try:
                bot_config = BotConfig.model_validate(await request.json())
            except json.JSONDecodeError:
                raise web.HTTPBadRequest(reason="Request body must be valid JSON")
            except pydantic.ValidationError as e:
                raise web.HTTPBadRequest(text=e.json(include_context=False, include_url=False))
            except Exception as e:
                raise web.HTTPBadRequest(reason=str(e))
            await self.bot_config_store.set_subkey(username, bot_name, bot_config)
            if existing_bot_config is None:
                return web.json_response(text=bot_config.model_dump_json(), status=201)
            else:
                return web.json_response(text=existing_bot_config.model_dump_json())

        @routes.get(self.URL_PREFIX + "/config/{bot_name}")
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

        @routes.delete(self.URL_PREFIX + "/config/{bot_name}")
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

        @routes.get(self.URL_PREFIX + "/config")
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

        @routes.post(self.URL_PREFIX + "/start/{bot_name}")
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
            try:
                bot_runner = await construct_bot(username, bot_name, bot_config)
            except Exception as e:
                raise web.HTTPBadRequest(reason=str(e))
            if await self.runner.start(username=username, bot_name=bot_name, bot_runner=bot_runner):
                await self.running_bots_store.add(username, bot_name)
                return web.Response(text="Bot started", status=201)
            else:
                return web.Response(text="Bot is already running")

        @routes.post(self.URL_PREFIX + "/stop/{bot_name}")
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

        @routes.get(self.URL_PREFIX + "/running")
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

        app.add_routes(routes)
        setup_swagger(app=app, swagger_url=f"{self.URL_PREFIX}/swagger")
        await self.auth.setup_routes(app)

    async def _ensure_running_bots(self) -> None:
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
                    bot_runner = await construct_bot(username=username, bot_name=bot_name, bot_config=bot_config)
                    await self.runner.start(username=username, bot_name=bot_name, bot_runner=bot_runner)
                except Exception:
                    logger.exception(f"Error creating bot {bot_name} ({username = })")

    # public methods to run constructor in different scenarios

    async def run_polling(self, port: int) -> None:
        """For standalone run"""
        logger.info("Running telebot constructor w/ polling")
        self._runner = PollingConstructedBotRunner()
        await self._ensure_running_bots()
        aiohttp_app = web.Application()
        await self.setup_routes(aiohttp_app)
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
        await self._ensure_running_bots()
        await self.setup_routes(webhook_app.aiohttp_app)
