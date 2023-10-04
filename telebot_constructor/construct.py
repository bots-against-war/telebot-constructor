import itertools
import logging
from typing import Callable, Coroutine, Optional

from telebot import AsyncTeleBot
from telebot.runner import AuxBotEndpoint, BotRunner
from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.banned_users import BannedUsersStore
from telebot_components.stores.generic import GenericStore
from telebot_components.utils.secrets import SecretStore

from telebot_constructor.bot_config import BotConfig
from telebot_constructor.group_chat_discovery import GroupChatDiscoveryHandler
from telebot_constructor.user_flow.types import BotCommandInfo
from telebot_constructor.utils.rate_limit_retry import rate_limit_retry

logger = logging.getLogger(__name__)

BotFactory = Callable[[str], AsyncTeleBot]


async def make_raw_bot(
    username: str, bot_config: BotConfig, secret_store: SecretStore, _bot_factory: BotFactory = AsyncTeleBot
) -> AsyncTeleBot:
    token = await secret_store.get_secret(secret_name=bot_config.token_secret_name, owner_id=username)
    if token is None:
        raise ValueError(f"Token name {bot_config.token_secret_name!r} does not correspond to a valid secret")
    return _bot_factory(token)


async def construct_bot(
    username: str,
    bot_name: str,
    bot_config: BotConfig,
    secret_store: SecretStore,
    redis: RedisInterface,
    group_chat_discovery_handler: Optional[GroupChatDiscoveryHandler] = None,
    _bot_factory: BotFactory = AsyncTeleBot,  # used for testing
) -> BotRunner:
    """Core bot construction function responsible for turning a config into a functional bot"""
    bot_prefix = f"{username}-{bot_name}"
    log_prefix = f"[{username}][{bot_name}] "
    logger.info(log_prefix + "Constructing bot")

    bot = await make_raw_bot(username=username, bot_config=bot_config, secret_store=secret_store, _bot_factory=_bot_factory)

    # HACK: this allows creating multiple bots with the same prefix, which is needed for hot reloading;
    # but this removes a failsafe mechanism and can cause problems with multiple competing bot instances
    GenericStore.allow_duplicate_stores(prefix=bot_prefix)

    background_jobs: list[Coroutine[None, None, None]] = []
    aux_endpoints: list[AuxBotEndpoint] = []
    bot_commands: list[BotCommandInfo] = []

    try:
        async for attempt in rate_limit_retry():
            with attempt:
                bot_user = await bot.get_me()
        logger.info(log_prefix + f"Bot user loaded: {bot_user.to_json()}")
    except Exception:
        logger.exception(log_prefix + "Error getting bot user, probably an invalid token")
        raise ValueError("Failed to get bot user with getMe, the token is probably invalid")

    banned_users_store = BannedUsersStore(redis=redis, bot_prefix=bot_prefix, cached=True)

    if bot_config.user_flow_config is not None:
        logger.info(log_prefix + "Parsing user flow config")
        user_flow = bot_config.user_flow_config.to_user_flow()

        logger.info(log_prefix + "Setting up user flow")
        user_flow_setup_result = await user_flow.setup(
            bot_prefix=bot_prefix,
            bot=bot,
            redis=redis,
            banned_users_store=banned_users_store,
        )

        logger.info(log_prefix + f"Got result: {user_flow_setup_result}")
        background_jobs.extend(user_flow_setup_result.background_jobs)
        aux_endpoints.extend(user_flow_setup_result.aux_endpoints)
        bot_commands.extend(user_flow_setup_result.bot_commands)

    # TODO: cleanup for possible stale bot commands (maybe on an explicit user action?)
    logger.info(f"Setting bot commands: {bot_commands}")
    for _, scoped_commands_it in itertools.groupby(
        sorted(
            bot_commands,
            key=BotCommandInfo.scope_key,
        ),
        key=BotCommandInfo.scope_key,
    ):
        command_info_batch = list(scoped_commands_it)
        logger.info(f"Bot command batch: {command_info_batch}")
        async for attempt in rate_limit_retry():
            with attempt:
                await bot.set_my_commands(
                    commands=[cmd.command for cmd in command_info_batch],
                    scope=command_info_batch[0].scope,
                )

    if group_chat_discovery_handler is not None:
        group_chat_discovery_handler.setup_handlers(username=username, bot_name=bot_name, bot=bot)

    return BotRunner(
        bot_prefix=bot_prefix,
        bot=bot,
        background_jobs=background_jobs,
        aux_endpoints=aux_endpoints,
    )
