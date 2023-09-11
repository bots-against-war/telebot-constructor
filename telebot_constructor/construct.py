import logging
from typing import Callable, Coroutine

from telebot import AsyncTeleBot
from telebot.runner import AuxBotEndpoint, BotRunner
from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.banned_users import BannedUsersStore
from telebot_components.stores.generic import GenericStore
from telebot_components.utils.secrets import SecretStore

from telebot_constructor.bot_config import BotConfig

logger = logging.getLogger(__name__)


async def construct_bot(
    username: str,
    bot_name: str,
    bot_config: BotConfig,
    secret_store: SecretStore,
    redis: RedisInterface,
    _bot_factory: Callable[[str], AsyncTeleBot] = AsyncTeleBot,  # used for testing
) -> BotRunner:
    """Core bot construction function responsible for turning a config into a functional bot"""
    log_prefix = f"[{username}][{bot_name}] "
    bot_prefix = f"{username}-{bot_name}"
    background_jobs: list[Coroutine[None, None, None]] = []
    aux_endpoints: list[AuxBotEndpoint] = []

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

    banned_users_store = BannedUsersStore(redis=redis, bot_prefix=bot_prefix, cached=True)

    if bot_config.user_flow_config is not None:
        logger.info(log_prefix + "Parsing user flow config")
        user_flow = bot_config.user_flow_config.to_user_flow()

        logger.info(log_prefix + f"Setting up user flow")
        user_flow_setup_result = await user_flow.setup(
            bot_prefix=bot_prefix,
            bot=bot,
            redis=redis,
            banned_users_store=banned_users_store,
        )

        logger.info(log_prefix + f"Got result: {user_flow_setup_result}")
        background_jobs.extend(user_flow_setup_result.background_jobs)
        aux_endpoints.extend(user_flow_setup_result.aux_endpoints)

    # HACK: this allows creating multiple bots with the same prefix, which is needed for hot reloading;
    # but this removes a failsafe mechanism and can cause problems with multiple competing bot instances
    GenericStore.allow_duplicate_stores(prefix=bot_prefix)

    return BotRunner(
        bot_prefix=bot_prefix,
        bot=bot,
        background_jobs=background_jobs,
        aux_endpoints=aux_endpoints,
    )
