from telebot import AsyncTeleBot
from telebot import types as tg
from telebot.runner import BotRunner

from telebot_constructor.bot_config import BotConfig


async def construct_bot(username: str, bot_name: str, bot_config: BotConfig) -> BotRunner:
    """Main heavy lifting function responsible for creating bot with all the necessary handlers / components / etc"""
    bot = AsyncTeleBot(token=bot_config.token)

    @bot.message_handler(commands=["start"])
    async def dummy_start_handler(message: tg.Message) -> None:
        await bot.reply_to(message, "hello world")

    try:
        await bot.get_me()
    except Exception:
        raise ValueError("Failed to getMe the bot, the token is probably invalid")

    return BotRunner(bot_prefix=f"{username}-{bot_name}", bot=bot)
