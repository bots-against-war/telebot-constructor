import abc
import asyncio
import collections

from telebot.runner import BotRunner


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
    """For standalone deployment without wrapping WebhookApp"""

    def __init__(self) -> None:
        self.running_bot_tasks: dict[str, dict[str, asyncio.Task[None]]] = collections.defaultdict(dict)

    async def start(self, username: str, bot_name: str, bot_runner: BotRunner) -> bool:
        if bot_name in self.running_bot_tasks.get(username, {}):
            return False

        bot_running_task = asyncio.create_task(bot_runner.run_polling(), name=f"{bot_name} by {username}")
        self.running_bot_tasks[username][bot_name] = bot_running_task
        bot_running_task.add_done_callback(lambda _task: self.running_bot_tasks[username].pop(bot_name, None))
        return True

    async def stop(self, username: str, bot_name: str) -> bool:
        bot_running_task = self.running_bot_tasks.get(username, {}).get(bot_name, None)
        if bot_running_task is None:
            return False
        else:
            return bot_running_task.cancel()

    async def cleanup(self) -> None:
        for _username, tasks in self.running_bot_tasks.items():
            for _bot_name, task in tasks.items():
                task.cancel()
                try:
                    await task
                except:
                    pass
