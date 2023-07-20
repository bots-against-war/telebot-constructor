import abc
import asyncio
import collections
import logging
from pathlib import Path
from typing import Optional

import telebot.api
from aiohttp import web
from telebot.runner import BotRunner
from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.generic import KeyDictStore

from telebot_constructor.construct import construct_bot

logger = logging.getLogger(__name__)


class ConstructedBotRunner(abc.ABC):
    @abc.abstractmethod
    async def start(self, username: str, bot_runner: BotRunner) -> bool:
        ...

    @abc.abstractmethod
    async def stop(self, username: str, bot_prefix: str) -> bool:
        ...

    @abc.abstractmethod
    async def cleanup(self) -> None:
        ...


class PollingConstructedBotRunner(ConstructedBotRunner):
    """For standalone deployment without wrapping WebhookApp"""

    def __init__(self) -> None:
        self.running_bot_tasks: dict[str, dict[str, asyncio.Task[None]]] = collections.defaultdict(dict)
        # TODO: store bot tokens in use to avoid polling the same bot from two bot runners

    async def start(self, username: str, bot_runner: BotRunner) -> bool:
        if bot_runner.bot_prefix in self.running_bot_tasks.get(username, {}):
            return False

        bot_running_task = asyncio.create_task(bot_runner.run_polling(), name=f"{username}-{bot_runner.bot_prefix}")
        self.running_bot_tasks[username][bot_runner.bot_prefix] = bot_running_task
        bot_running_task.add_done_callback(
            lambda _task: self.running_bot_tasks[username].pop(bot_runner.bot_prefix, None)
        )
        return True

    async def stop(self, username: str, bot_prefix: str) -> bool:
        bot_running_task = self.running_bot_tasks.get(username, {}).get(bot_prefix, None)
        if bot_running_task is None:
            return False
        else:
            return bot_running_task.cancel()

    async def cleanup(self) -> None:
        for _username, tasks in self.running_bot_tasks.items():
            for _bot_prefix, task in tasks.items():
                task.cancel()
                try:
                    await task
                except:
                    pass


class TelebotConstructorApp:
    STORE_PREFIX = "telebot-constructor"

    def __init__(self, redis: RedisInterface) -> None:
        # user id -> {bot prefix -> config}
        self.bot_config_storage = KeyDictStore[dict](name="bot-config", prefix=self.STORE_PREFIX, redis=redis)
        self._runner: Optional[ConstructedBotRunner] = None

    @property
    def runner(self) -> ConstructedBotRunner:
        if self._runner is None:
            raise RuntimeError("Constructed bot runner was not initialized properly")
        return self._runner

    async def authenticate(self, request: web.Request) -> str:
        return "admin"  # TODO: user id lookup based on access token / other auth method

    def create_routes(self) -> web.RouteTableDef:
        routes = web.RouteTableDef()

        # bot config CRUD
        @routes.get("/")
        async def index(request: web.Request) -> web.Response:
            static_dir = Path(__file__).parent / "../frontend/public"
            return web.Response(body=(static_dir / "index.html").read_bytes(), content_type="text/html")

        @routes.post("/config")
        async def create_bot_config(request: web.Request) -> web.Response:
            username = await self.authenticate(request)
            bot_config = await request.json()
            # TODO: pydantic validation for config
            # TODO: do not store bot token in config directly, use secrets
            bot_prefix = bot_config["prefix"]
            await self.bot_config_storage.set_subkey(username, bot_prefix, bot_config)
            return web.Response(text="OK")

        @routes.get("/config")
        async def list_bot_configs(request: web.Request) -> web.Response:
            username = await self.authenticate(request)
            bot_configs = await self.bot_config_storage.list_values(username)
            return web.json_response(data=bot_configs)

        # TODO: other update & delete...

        # bot start / stop

        @routes.post("/start/{bot_prefix}")
        async def stop_bot(request: web.Request) -> web.Response:
            username = await self.authenticate(request)
            bot_prefix = request.match_info.get("bot_prefix")
            if bot_prefix is None:
                raise web.HTTPNotFound()
            bot_config = await self.bot_config_storage.get_subkey(username, bot_prefix)
            if bot_config is None:
                raise web.HTTPNotFound()
            bot_runner = await construct_bot(bot_config)
            if await self.runner.start(username=username, bot_runner=bot_runner):
                return web.Response(text="OK")
            else:
                return web.Response(text="Already running")

        @routes.post("/stop/{bot_prefix}")
        async def stop_bot(request: web.Request) -> web.Response:
            username = await self.authenticate(request)
            bot_prefix = request.match_info.get("bot_prefix")
            if bot_prefix is None:
                raise web.HTTPNotFound()
            if await self.runner.stop(username=username, bot_prefix=bot_prefix):
                return web.Response(text="OK")
            else:
                return web.Response(text="Bot not running")

        return routes

    # public methods to run constructor in different scenarios

    async def run_polling(self, port: int) -> None:
        """For standalone run"""
        logger.info("Running telebot constructor w/ polling")
        self._runner = PollingConstructedBotRunner()

        #########################################################################
        # TODO: this can be slow for large amount of users! parallelize
        usernames = await self.bot_config_storage.list_keys()
        logger.info("Found %s usernames with bots", len(usernames))
        for username in usernames:
            bot_configs = await self.bot_config_storage.list_values(username)
            logger.info("Username %s has %s bots", usernames, len(bot_configs))
            for bot_config in bot_configs:
                bot_runner = await construct_bot(config=bot_config)
                await self.runner.start(username=username, bot_runner=bot_runner)
        #########################################################################

        aiohttp_app = web.Application()
        aiohttp_app.add_routes(self.create_routes())
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
