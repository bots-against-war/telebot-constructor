import asyncio

from aioresponses import aioresponses
from telebot.runner import BotRunner
from telebot.test_util import MockedAsyncTeleBot
from yarl import URL

from telebot_constructor.runners import PollingConstructedBotRunner


async def test_polling_bot_runner() -> None:
    runner = PollingConstructedBotRunner()
    bot_runner = BotRunner(
        bot_prefix="bot-prefix",
        bot=MockedAsyncTeleBot("TOKEN"),
    )
    with aioresponses() as mock:
        mock.get("https://api.telegram.org/botTOKEN/getUpdates", repeat=True, payload={"ok": True, "result": []})

        await runner.start(
            username="user",
            bot_name="bot",
            bot_runner=bot_runner,
        )
        await asyncio.sleep(0.1)
        assert ("get", URL("https://api.telegram.org/botTOKEN/getUpdates")) in mock.requests
        await runner.stop(username="user", bot_name="bot")

        await runner.start(
            username="user",
            bot_name="bot",
            bot_runner=bot_runner,
        )
        await asyncio.sleep(0.1)
        assert ("get", URL("https://api.telegram.org/botTOKEN/getUpdates")) in mock.requests
        await runner.stop(username="user", bot_name="bot")
