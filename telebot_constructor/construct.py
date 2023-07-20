from typing import Any

from telebot import AsyncTeleBot
from telebot import types as tg
from telebot.runner import BotRunner


async def construct_bot(config: Any) -> BotRunner:
    """Main heavy lifting function responsible for creating bot with all the necessary handlers / components / etc"""
    bot = AsyncTeleBot(token=config["token"])

    @bot.message_handler(commands=["start"])
    async def dummy_start_handler(message: tg.Message) -> None:
        await bot.reply_to(message, "hello world")

    return BotRunner(bot_prefix=config["prefix"], bot=bot)
