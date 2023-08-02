from telebot import AsyncTeleBot
import logging
from telebot import types as tg
from telebot.runner import BotRunner

from telebot_constructor.bot_config import BotConfig
from telebot_components.utils.secrets import SecretStore

logger = logging.getLogger(__name__)


async def construct_bot(username: str, bot_name: str, bot_config: BotConfig, secret_store: SecretStore) -> BotRunner:
    """Core bot construction function responsible for turning a config into a functional bot"""
    log_prefix = f"[{username}][{bot_name}] "

    logger.info(log_prefix + "Constructing bot")

    token = await secret_store.get_secret(bot_config.token_secret_name)
    if token is None:
        raise ValueError(f"Token name {bot_config.token_secret_name} does not correspond to a valid secret")
    logger.info(log_prefix + "Loaded token from the secret store")
    bot = AsyncTeleBot(token=token)

    try:
        bot_user = await bot.get_me()
        logger.info(log_prefix + f"Bot user loaded: {bot_user.to_json()}")
    except Exception:
        logger.exception(log_prefix + "Error getting bot user, probably an invalid token")
        raise ValueError("Failed to get bot user with getMe, the token is probably invalid")

    # handlers setup (dummy)

    @bot.message_handler(commands=["start"])
    async def dummy_start_handler(message: tg.Message) -> None:
        await bot.reply_to(message, "hello world")

    return BotRunner(bot_prefix=f"{username}-{bot_name}", bot=bot)
