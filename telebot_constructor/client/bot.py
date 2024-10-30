from telebot import AsyncTeleBot
from telebot import types as tg
from telebot.types import constants as tgconst
from telebot_components.redis_utils.interface import RedisInterface
from telebot.runner import BotRunner

from telebot_constructor.client.client import TelebotConstructorClient


async def create_telebot_constructor_client_bot(
    redis: RedisInterface,
    client: TelebotConstructorClient,
    bot_token: str,
    constructor_base_url: str,
    bot_prefix: str = "telebot-constructor-client",
) -> BotRunner:
    """Simple bot interface to telebot constructor, providing livegram-like frontend to create feedback bots"""
    bot = AsyncTeleBot(token=bot_token)

    @bot.message_handler(commands=["start"], chat_types=[tgconst.ChatType.private])
    async def start_bot(m: tg.Message) -> None:
        await bot.send_message(
            chat_id=m.chat.id,
            text=f'Hi! This is a simple interface for <a href="{constructor_base_url}">Telebot Constructor</a>.'
            + "\n\n/newbot – create a simple feedback bot\n/mybots – list my bots",
        )

    @bot.message_handler(commands=["mybots"], chat_types=[tgconst.ChatType.private])
    async def list_my_bots(m: tg.Message) -> None:
        pass

    return BotRunner(bot_prefix=bot_prefix, bot=bot)
