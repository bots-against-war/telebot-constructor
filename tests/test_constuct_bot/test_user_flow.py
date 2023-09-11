import pytest
from telebot.test_util import MockedAsyncTeleBot
from telebot_components.redis_utils.emulation import RedisEmulation

from telebot_constructor.bot_config import (
    BotConfig,
    UserFlowBlockConfig,
    UserFlowConfig,
    UserFlowEntryPointConfig,
)
from telebot_constructor.construct import construct_bot
from telebot_constructor.user_flow.blocks.human_operator import (
    FeedbackHandlerConfig,
    HumanOperatorBlock,
    MessagesToAdmin,
    MessagesToUser,
)
from telebot_constructor.user_flow.blocks.message import MessageBlock
from telebot_constructor.user_flow.entrypoints.command import CommandEntryPoint
from tests.utils import (
    assert_method_call_kwargs_include,
    dummy_secret_store,
    tg_update_message_to_bot,
)


def test_user_flow_config_model_validation() -> None:
    with pytest.raises(ValueError, match=r".*?Duplicate block ids: \['1'\]"):
        UserFlowConfig(
            entrypoints=[],
            blocks=[
                UserFlowBlockConfig(
                    message=MessageBlock(block_id="1", message_text="one", next_block_id=None), human_operator=None
                ),
                UserFlowBlockConfig(
                    message=MessageBlock(block_id="1", message_text="also one", next_block_id=None), human_operator=None
                ),
            ],
            node_display_coords={},
        )


async def test_simple_user_flow() -> None:
    bot_config = BotConfig(
        token_secret_name="token",
        display_name="Test bot",
        user_flow_config=UserFlowConfig(
            entrypoints=[
                UserFlowEntryPointConfig(
                    command=CommandEntryPoint(
                        entrypoint_id="command-1",
                        command="hello",
                        next_block_id="message-1",
                    ),
                )
            ],
            blocks=[
                UserFlowBlockConfig(
                    message=MessageBlock(
                        block_id="message-1",
                        message_text="hello!",
                        next_block_id="message-2",
                    ),
                    human_operator=None,
                ),
                UserFlowBlockConfig(
                    message=MessageBlock(
                        block_id="message-2",
                        message_text="how are you today?",
                        next_block_id=None,
                    ),
                    human_operator=None,
                ),
            ],
            node_display_coords={},
        ),
    )

    redis = RedisEmulation()
    secret_store = dummy_secret_store(redis)
    username = "user123"
    await secret_store.save_secret(secret_name="token", secret_value="mock-token", owner_id=username)
    bot_runner = await construct_bot(
        username=username,
        bot_name="simple-user-flow-bot",
        bot_config=bot_config,
        secret_store=secret_store,
        redis=redis,
        _bot_factory=MockedAsyncTeleBot,
    )

    assert not bot_runner.background_jobs
    assert not bot_runner.aux_endpoints

    bot = bot_runner.bot
    assert isinstance(bot, MockedAsyncTeleBot)
    await bot.process_new_updates([tg_update_message_to_bot(user_id=1312, first_name="User", text="/hello")])
    assert len(bot.method_calls) == 2
    assert_method_call_kwargs_include(
        bot.method_calls["send_message"],
        [
            {"chat_id": 1312, "text": "hello!"},
            {"chat_id": 1312, "text": "how are you today?"},
        ],
    )


@pytest.mark.parametrize("catch_all", [True, False])
async def test_flow_with_human_operator(catch_all: bool) -> None:
    ADMIN_CHAT_ID = 98765
    USER_ID = 1312
    bot_config = BotConfig(
        token_secret_name="token",
        display_name="Simple feedback bot",
        user_flow_config=UserFlowConfig(
            entrypoints=[
                UserFlowEntryPointConfig(
                    command=CommandEntryPoint(
                        entrypoint_id="command-1",
                        command="start",
                        next_block_id="message-1",
                    ),
                )
            ],
            blocks=[
                UserFlowBlockConfig(
                    message=MessageBlock(
                        block_id="message-1",
                        message_text="Hi, I'm a bot",
                        next_block_id="human-operator-1",
                    ),
                    human_operator=None,
                ),
                UserFlowBlockConfig(
                    message=None,
                    human_operator=HumanOperatorBlock(
                        block_id="human-operator-1",
                        catch_all=catch_all,
                        feedback_handler_config=FeedbackHandlerConfig(
                            admin_chat_id=ADMIN_CHAT_ID,
                            forum_topic_per_user=False,
                            messages_to_user=MessagesToUser(forwarded_to_admin_ok="ok", throttling=""),
                            messages_to_admin=MessagesToAdmin(
                                copied_to_user_ok="copied ok", deleted_message_ok="", can_not_delete_message=""
                            ),
                            anonimyze_users=False,
                            max_messages_per_minute=10,
                            hashtags_in_admin_chat=True,
                            unanswered_hashtag="unanswered",
                            hashtag_message_rarer_than=None,
                            message_log_to_admin_chat=True,
                        ),
                    ),
                ),
            ],
            node_display_coords={},
        ),
    )

    redis = RedisEmulation()
    secret_store = dummy_secret_store(redis)
    username = "user123"
    await secret_store.save_secret(secret_name="token", secret_value="mock-token", owner_id=username)
    bot_runner = await construct_bot(
        username=username,
        bot_name="simple-user-flow-bot",
        bot_config=bot_config,
        secret_store=secret_store,
        redis=redis,
        _bot_factory=MockedAsyncTeleBot,
    )

    assert not bot_runner.background_jobs
    assert not bot_runner.aux_endpoints

    bot = bot_runner.bot
    assert isinstance(bot, MockedAsyncTeleBot)
    bot.method_calls.clear()  # remove construct-time calls

    # direct message to bot but not a command
    await bot.process_new_updates(
        [tg_update_message_to_bot(user_id=USER_ID, first_name="User", text="hello i am user")]
    )
    if catch_all:
        assert_method_call_kwargs_include(
            bot.method_calls["send_message"],
            [
                {"chat_id": ADMIN_CHAT_ID, "text": "#unanswered"},  # hashtag in admin chat
                {
                    "chat_id": ADMIN_CHAT_ID,
                    "text": '<a href="tg://user?id=1312">User (#1312)</a>',
                    "parse_mode": "HTML",
                },  # user identifier in admin chat
                {"chat_id": USER_ID, "text": "ok"},  # reply to user
            ],
        )
        assert_method_call_kwargs_include(
            bot.method_calls["copy_message"],
            [
                {"chat_id": ADMIN_CHAT_ID, "from_chat_id": USER_ID},
            ],
        )
    else:
        # no response, human operator block is not active
        assert len(bot.method_calls) == 0
    bot.method_calls.clear()

    # /start command
    await bot.process_new_updates([tg_update_message_to_bot(user_id=USER_ID, first_name="User", text="/start")])
    assert_method_call_kwargs_include(
        bot.method_calls["send_message"],
        [
            {"chat_id": USER_ID, "text": "Hi, I'm a bot"},
        ],
    )
    bot.method_calls.clear()

    # message to bot after the command
    await bot.process_new_updates(
        [tg_update_message_to_bot(user_id=USER_ID, first_name="User", text="hello i am user")]
    )
    if catch_all:
        assert_method_call_kwargs_include(
            bot.method_calls["send_message"],
            [
                {"chat_id": USER_ID, "text": "ok"},  # reply to user
            ],
        )
    else:
        assert_method_call_kwargs_include(
            bot.method_calls["send_message"],
            [
                {"chat_id": ADMIN_CHAT_ID, "text": "#unanswered"},  # hashtag in admin chat
                {
                    "chat_id": ADMIN_CHAT_ID,
                    "text": '<a href="tg://user?id=1312">User (#1312)</a>',
                    "parse_mode": "HTML",
                },  # user identifier in admin chat
                {"chat_id": USER_ID, "text": "ok"},  # reply to user
            ],
        )

    assert_method_call_kwargs_include(
        bot.method_calls["copy_message"],
        [
            {"chat_id": ADMIN_CHAT_ID, "from_chat_id": USER_ID},
        ],
    )
