import logging

from telebot import AsyncTeleBot
from telebot import types as tg
from telebot.runner import BotRunner
from telebot_components.utils.secrets import SecretStore
from telebot_components.constants import times
from telebot_components.feedback import FeedbackHandler, FeedbackConfig, UserAnonymization, AntiSpam, AntiSpamConfig, \
    ServiceMessages
from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.banned_users import BannedUsersStore

from telebot_constructor.bot_config import BotConfig

logger = logging.getLogger(__name__)


async def construct_bot(username: str, bot_name: str, bot_config: BotConfig, secret_store: SecretStore, redis: RedisInterface) -> BotRunner:
    """Core bot construction function responsible for turning a config into a functional bot"""
    log_prefix = f"[{username}][{bot_name}] "
    bot_prefix = f"{username}-{bot_name}"

    logger.info(log_prefix + "Constructing bot")

    token = await secret_store.get_secret(secret_name=bot_config.token_secret_name, owner_id=username)  # type: ignore
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

    banned_store = BannedUsersStore(
        redis,
        bot_prefix,
        cached=False,
    )

    @bot.message_handler(commands=["start"], func=banned_store.not_from_banned_user)
    async def dummy_start_handler(message: tg.Message) -> None:
        await bot.reply_to(message, "hello world")

    # region Feedback
    feedback_handler = FeedbackHandler(
        admin_chat_id=bot_config.admin_chat_id,
        redis=redis,
        bot_prefix=bot_prefix,
        config=FeedbackConfig(
            message_log_to_admin_chat=True,
            force_category_selection=False,
            hashtags_in_admin_chat=True,
            hashtag_message_rarer_than=times.FIVE_MINUTES,
            unanswered_hashtag="unanswered",
            confirm_forwarded_to_admin_rarer_than=times.FIVE_MINUTES,
            user_anonymization=UserAnonymization.NONE,
        ),
        anti_spam=AntiSpam(
            redis,
            bot_prefix,
            config=AntiSpamConfig(
                throttle_after_messages=3,
                throttle_duration=times.FIVE_MINUTES,
                soft_ban_after_throttle_violations=5,
                soft_ban_duration=times.HOUR,
            ),
        ),
        service_messages=ServiceMessages(
            forwarded_to_admin_ok="Forwarded!",
            you_must_select_category="Please select category first!",
            throttling_template="⚠ Please send no more than {} messages in {}.",
            copied_to_user_ok="Copied to user chat ✨",
            can_not_delete_message="Unable to delete message.",
            deleted_message_ok="Message successfully deleted!",
        ),
    )
    await feedback_handler.setup(bot)
    # endregion

    return BotRunner(
        bot_prefix=bot_prefix,
        bot=bot,
        background_jobs=feedback_handler.background_jobs(base_url=None, server_listening_future=None),
    )
