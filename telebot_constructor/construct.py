import logging
from typing import Callable, Coroutine

from telebot import AsyncTeleBot
from telebot import types as tg
from telebot.runner import BotRunner
from telebot_components.constants import times
from telebot_components.feedback import (
    AntiSpam,
    AntiSpamConfig,
    FeedbackConfig,
    FeedbackHandler,
    ServiceMessages,
    UserAnonymization,
)
from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.generic import GenericStore
from telebot_components.utils.secrets import SecretStore

from telebot_constructor.bot_config import BotConfig
from telebot_constructor.user_flow.types import UserFlowSetupContext

logger = logging.getLogger(__name__)


async def construct_bot(
    username: str,
    bot_name: str,
    bot_config: BotConfig,
    secret_store: SecretStore,
    redis: RedisInterface,
    _bot_factory: Callable[[str], AsyncTeleBot] = AsyncTeleBot,
) -> BotRunner:
    """Core bot construction function responsible for turning a config into a functional bot"""
    log_prefix = f"[{username}][{bot_name}] "
    bot_prefix = f"{username}-{bot_name}"
    background_jobs: list[Coroutine[None, None, None]] = []

    logger.info(log_prefix + "Constructing bot")

    token = await secret_store.get_secret(secret_name=bot_config.token_secret_name, owner_id=username)
    if token is None:
        raise ValueError(f"Token name {bot_config.token_secret_name!r} does not correspond to a valid secret")
    logger.info(log_prefix + f"Loaded token from the secret store, secret {bot_config.token_secret_name!r}")
    bot = _bot_factory(token)

    try:
        bot_user = await bot.get_me()
        logger.info(log_prefix + f"Bot user loaded: {bot_user.to_json()}")
    except Exception:
        logger.exception(log_prefix + "Error getting bot user, probably an invalid token")
        raise ValueError("Failed to get bot user with getMe, the token is probably invalid")

    # region Feedback

    feedback_config = bot_config.feedback_handler_config
    if feedback_config:
        logger.info(log_prefix + "Setting up feedback handler")
        feedback_handler = FeedbackHandler(
            admin_chat_id=feedback_config.admin_chat_id,
            redis=redis,
            bot_prefix=bot_prefix,
            config=FeedbackConfig(
                message_log_to_admin_chat=feedback_config.message_log_to_admin_chat,
                force_category_selection=feedback_config.force_category_selection,
                hashtags_in_admin_chat=feedback_config.hashtags_in_admin_chat,
                hashtag_message_rarer_than=feedback_config.hashtag_message_rarer_than,
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
        background_jobs.extend(feedback_handler.background_jobs(base_url=None, server_listening_future=None))

    # endregion
    if bot_config.user_flow_config is not None:
        user_flow = bot_config.user_flow_config.to_user_flow()
        await user_flow.setup(
            context=UserFlowSetupContext(
                bot=bot,
                redis=redis,
            )
        )

    # HACK: this allows creating multiple bots with the same prefix, which is needed for hot reloading;
    # but this removes a failsafe mechanism and can cause problems with multiple competing bot instances
    GenericStore.allow_duplicate_stores(prefix=bot_prefix)

    return BotRunner(
        bot_prefix=bot_prefix,
        bot=bot,
        background_jobs=background_jobs,
    )
