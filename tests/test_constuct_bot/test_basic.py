import pytest
from aioresponses import aioresponses
from telebot.test_util import MockedAsyncTeleBot
from telebot_components.redis_utils.emulation import RedisEmulation

from telebot_constructor.bot_config import BotConfig
from telebot_constructor.construct import construct_bot
from tests.utils import dummy_secret_store


async def test_construct_empty_bot() -> None:
    redis = RedisEmulation()
    secret_store = dummy_secret_store(redis)
    username = "test-user"
    await secret_store.save_secret(secret_name="empty-bot-token", secret_value="mock-token", owner_id=username)
    await construct_bot(
        username=username,
        bot_name="empty-bot-test",
        bot_config=BotConfig(token_secret_name="empty-bot-token", display_name="Test bot"),
        secret_store=secret_store,
        redis=redis,
        _bot_factory=MockedAsyncTeleBot,
    )


async def test_missing_token_secret() -> None:
    redis = RedisEmulation()
    with pytest.raises(ValueError):
        await construct_bot(
            username="some-user",
            bot_name="bot-test",
            bot_config=BotConfig(token_secret_name="empty-bot-token", display_name="Test bot"),
            secret_store=dummy_secret_store(redis),
            redis=redis,
            _bot_factory=MockedAsyncTeleBot,
        )


async def test_bot_token_validation_failed() -> None:
    redis = RedisEmulation()
    secret_store = dummy_secret_store(redis)
    username = "test-user"
    await secret_store.save_secret(secret_name="token", secret_value="123456789", owner_id=username)
    with aioresponses() as mock_http:
        mock_http.get("https://api.telegram.org/bot123456789/getMe", status=404, repeat=True)
        with pytest.raises(ValueError, match="Failed to get bot user with getMe, the token is probably invalid"):
            await construct_bot(
                username=username,
                bot_name="test",
                bot_config=BotConfig(token_secret_name="token", display_name="Test bot"),
                secret_store=secret_store,
                redis=redis,
            )
