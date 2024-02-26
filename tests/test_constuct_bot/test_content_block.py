import time

from telebot import types as tg
from telebot.test_util import MockedAsyncTeleBot
from telebot_components.redis_utils.emulation import RedisEmulation

from telebot_constructor.bot_config import (
    BotConfig,
    UserFlowBlockConfig,
    UserFlowConfig,
    UserFlowEntryPointConfig,
)
from telebot_constructor.construct import construct_bot
from telebot_constructor.user_flow.blocks.content import (
    Content,
    ContentBlock,
    ContentBlockContentAttachment,
    ContentText,
    ContentTextMarkup,
)
from telebot_constructor.user_flow.entrypoints.command import CommandEntryPoint
from tests.utils import (
    assert_method_call_kwargs_include,
    dummy_secret_store,
    tg_update_message_to_bot,
)


async def test_single_photo() -> None:
    # simple bot config with a single /start leading to a single content block
    bot_config = BotConfig(
        token_secret_name="token",
        display_name="Content block test bot",
        user_flow_config=UserFlowConfig(
            entrypoints=[
                UserFlowEntryPointConfig(
                    command=CommandEntryPoint(
                        entrypoint_id="command-1",
                        command="start",
                        next_block_id="content-1",
                        short_description="start cmd",
                    ),
                )
            ],
            blocks=[
                UserFlowBlockConfig(
                    content=ContentBlock(
                        block_id="content-1",
                        contents=[
                            Content(
                                text=ContentText(text="photo caption", markup=ContentTextMarkup.HTML),
                                attachments=[ContentBlockContentAttachment(image="base64-string")],
                            )
                        ],
                        next_block_id=None,
                    ),
                ),
            ],
            node_display_coords={},
        ),
    )

    # setting up dependencies with in-memory redis emulation
    redis = RedisEmulation()
    secret_store = dummy_secret_store(redis)

    # creating "secret" with bot token (in prod it is done automatically during bot creation)
    username = "test-username"
    await secret_store.save_secret(secret_name="token", secret_value="<token>", owner_id=username)

    # calling main constructor function, in prod it is done when starting the bot (see /api/start/{bot_name})
    bot_runner = await construct_bot(
        username=username,
        bot_name="simple-user-flow-bot",
        bot_config=bot_config,
        secret_store=secret_store,
        redis=redis,
        # for tests we use "mocked" bot class instead of the real one; it will not make any requests
        # to Telegram, but store calls so that we can check them as part of the test (see below)
        _bot_factory=MockedAsyncTeleBot,
    )

    bot = bot_runner.bot
    assert isinstance(bot, MockedAsyncTeleBot)  # just for typing
    # method_calls is a special property existing only on mocked bot class, it stores
    # all calls made on this bot instance; here we clear it, because during setup constructor
    # already made some calls (e.g. getMe) and we're not interested in them in this test
    bot.method_calls.clear()

    # here we imitate user-bot interaction (in prod it would be done when bot receives updates
    # from Telegram, here we do it manually); we have to specify in advance which value bot
    # should receive from Telegram here
    def set_return_for_send_photo():
        bot.add_return_values(
            "send_photo",
            tg.Message(
                message_id=1,
                from_user=tg.User(id=1, is_bot=True, first_name="Bot"),
                date=int(time.time()),
                chat=None,  # type: ignore
                content_type="photo",
                options={
                    "photo": [
                        tg.PhotoSize(
                            file_id="example-file-id",
                            file_unique_id="unused",
                            width=100,
                            height=100,
                        )
                    ]
                },
                json_string={},
            ),
        )

    # first interaction with bot -- it whould send photo as raw bytes, recieve file_id and save it to cache
    set_return_for_send_photo()
    await bot.process_new_updates([tg_update_message_to_bot(user_id=111111, first_name="User", text="/start")])

    # check that the bot responds to this message as expected (sends photo in this case)
    assert len(bot.method_calls) == 1
    assert_method_call_kwargs_include(
        bot.method_calls["send_photo"],
        [
            {
                "caption": "photo caption",
                "photo": b"m\xab\x1e\xeb\x8b-\xae)\xe0",
                "chat_id": 111111,
                "parse_mode": "HTML",
            },
        ],
    )
    bot.method_calls.clear()

    # second interaction should be the same, but the bot finds a cached file_id for the photo and sends it instead
    # of uploading raw bytes second time
    set_return_for_send_photo()
    await bot.process_new_updates([tg_update_message_to_bot(user_id=111111, first_name="User", text="/start")])
    assert len(bot.method_calls) == 1
    assert_method_call_kwargs_include(
        bot.method_calls["send_photo"],
        [
            {
                "caption": "photo caption",
                "photo": "example-file-id",
                "chat_id": 111111,
                "parse_mode": "HTML",
            },
        ],
    )
    bot.method_calls.clear()
