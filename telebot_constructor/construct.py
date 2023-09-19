import datetime
import itertools
import logging
from typing import Callable, Coroutine, cast

import tenacity
from telebot import AsyncTeleBot
from telebot import api as tg_api
from telebot import types as tg
from telebot.runner import AuxBotEndpoint, BotRunner
from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.banned_users import BannedUsersStore
from telebot_components.stores.generic import GenericStore
from telebot_components.utils.secrets import SecretStore
from tenacity import RetryCallState
from tenacity.retry import (
    retry_all,
    retry_if_exception_message,
    retry_if_exception_type,
)
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_chain, wait_exponential

from telebot_constructor.bot_config import BotConfig
from telebot_constructor.user_flow.types import BotCommandInfo

logger = logging.getLogger(__name__)


class wait_from_too_many_requests_error(tenacity.wait.wait_base):
    def __call__(self, retry_state: RetryCallState) -> float:
        if retry_state.outcome is None:
            return 0.0
        if not retry_state.outcome.failed:
            return 0.0
        exc = cast(Exception, retry_state.outcome.exception())
        if not isinstance(exc, tg_api.ApiHTTPException):
            return 0.0
        if exc.error_parameters is None or exc.error_parameters.retry_after is None:
            return 0.0
        return exc.error_parameters.retry_after


def rate_limit_retry():
    return tenacity.AsyncRetrying(
        retry=retry_all(
            retry_if_exception_type(tg_api.ApiHTTPException),
            retry_if_exception_message(match="Too Many Requests"),
        ),
        wait=wait_chain(
            wait_from_too_many_requests_error(),
            wait_exponential(
                multiplier=1,
                max=datetime.timedelta(minutes=3),
                min=datetime.timedelta(seconds=1),
            ),
        ),
        stop=stop_after_attempt(5),
        reraise=True,
    )


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
    bot_commands: list[BotCommandInfo] = []

    logger.info(log_prefix + "Constructing bot")

    token = await secret_store.get_secret(secret_name=bot_config.token_secret_name, owner_id=username)
    if token is None:
        raise ValueError(f"Token name {bot_config.token_secret_name!r} does not correspond to a valid secret")
    logger.info(log_prefix + f"Loaded token from the secret store, secret {bot_config.token_secret_name!r}")
    bot = _bot_factory(token)

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

    # HACK: this allows creating multiple bots with the same prefix, which is needed for hot reloading;
    # but this removes a failsafe mechanism and can cause problems with multiple competing bot instances
    GenericStore.allow_duplicate_stores(prefix=bot_prefix)

    return BotRunner(
        bot_prefix=bot_prefix,
        bot=bot,
        background_jobs=background_jobs,
        aux_endpoints=aux_endpoints,
    )
