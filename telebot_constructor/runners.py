import abc
import asyncio
import collections
import logging

import telebot.api
from telebot.runner import BotRunner
from telebot.webhook import WebhookApp


class ConstructedBotRunner(abc.ABC):
    @abc.abstractmethod
    async def start(self, username: str, bot_name: str, bot_runner: BotRunner) -> bool:
        ...

    @abc.abstractmethod
    async def stop(self, username: str, bot_name: str) -> bool:
        ...

    @abc.abstractmethod
    async def cleanup(self) -> None:
        ...


class PollingConstructedBotRunner(ConstructedBotRunner):
    """Runner for standalone deployment without wrapping into WebhookApp"""

    def __init__(self) -> None:
        self.running_bot_tasks: dict[str, dict[str, asyncio.Task[None]]] = collections.defaultdict(dict)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__qualname__}")

    async def start(self, username: str, bot_name: str, bot_runner: BotRunner) -> bool:
        if bot_name in self.running_bot_tasks.get(username, {}):
            return False

        bot_running_task = asyncio.create_task(bot_runner.run_polling(), name=f"{bot_name} by {username}")
        self.running_bot_tasks[username][bot_name] = bot_running_task
        bot_running_task.add_done_callback(lambda _task: self.running_bot_tasks[username].pop(bot_name, None))
        return True

    async def stop(self, username: str, bot_name: str) -> bool:
        bot_running_task = self.running_bot_tasks.get(username, {}).pop(bot_name, None)
        if bot_running_task is None:
            return False
        else:
            is_cancelled = bot_running_task.cancel()
            if not is_cancelled:
                return False
            try:
                await bot_running_task
            except asyncio.CancelledError:
                # HACK: telebot's infinity polling closes HTTP session on polling stop,
                #       so here we forcefully recreate it
                await telebot.api.session_manager.get_session()
            return True

    async def cleanup(self) -> None:
        for bot_tasks in list(self.running_bot_tasks.values()):
            for task in list(bot_tasks.values()):
                task.cancel()


class WebhookAppConstructedBotRunner(ConstructedBotRunner):
    """Runner for integrating constructed bots into an existing webhook app"""

    def __init__(self, webhook_app: WebhookApp) -> None:
        self.webhook_app = webhook_app
        self.added_runners: dict[str, dict[str, BotRunner]] = collections.defaultdict(dict)

    async def start(self, username: str, bot_name: str, bot_runner: BotRunner) -> bool:
        if await self.webhook_app.add_bot_runner(bot_runner):
            self.added_runners[username][bot_name] = bot_runner
            return True
        else:
            return False

    async def stop(self, username: str, bot_name: str) -> bool:
        bot_runner = self.added_runners.get(username, {}).get(bot_name)
        if bot_runner is None:
            return False
        else:
            return await self.webhook_app.remove_bot_runner(bot_runner)

    async def cleanup(self) -> None:
        """All bots are cleaned up by the webhook app itweslf, no need to do anything"""
        pass
