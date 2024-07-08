import base64
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
    dummy_form_results_store,
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
        bot_id="simple-user-flow-bot",
        bot_config=bot_config,
        form_results_store=dummy_form_results_store(),
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


async def test_multiple_photos() -> None:
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
                                text=ContentText(text="photo album for u", markup=ContentTextMarkup.HTML),
                                attachments=[
                                    ContentBlockContentAttachment(image=base64.b64encode(b"base64-string-1").decode()),
                                    ContentBlockContentAttachment(image=base64.b64encode(b"base64-string-2").decode()),
                                ],
                            )
                        ],
                        next_block_id=None,
                    ),
                ),
            ],
            node_display_coords={},
        ),
    )

    redis = RedisEmulation()
    secret_store = dummy_secret_store(redis)

    username = "test-username"
    await secret_store.save_secret(secret_name="token", secret_value="<token>", owner_id=username)

    bot_runner = await construct_bot(
        username=username,
        bot_id="multiple-photos-in-content-block",
        bot_config=bot_config,
        form_results_store=dummy_form_results_store(),
        secret_store=secret_store,
        redis=redis,
        _bot_factory=MockedAsyncTeleBot,
    )
    bot = bot_runner.bot
    assert isinstance(bot, MockedAsyncTeleBot)
    bot.method_calls.clear()

    def set_return_for_send_photo(bot: MockedAsyncTeleBot, response_file_ids: list[str]):
        bot.add_return_values(
            "send_media_group",
            [
                tg.Message(
                    message_id=1312,
                    from_user=tg.User(id=161, is_bot=True, first_name="Bot"),
                    date=int(time.time()),
                    chat=None,  # type: ignore
                    content_type="photo",
                    options={
                        "photo": [
                            tg.PhotoSize(
                                file_id=file_id,
                                file_unique_id="unused",
                                width=100,
                                height=100,
                            )
                        ]
                    },
                    json_string={},
                )
                for file_id in response_file_ids
            ],
        )

    set_return_for_send_photo(bot, ["file-id-1", "file-id-2"])
    await bot.process_new_updates([tg_update_message_to_bot(user_id=1900, first_name="User", text="/start")])
    assert len(bot.method_calls) == 1
    media_group_calls = bot.method_calls["send_media_group"]
    assert len(media_group_calls) == 1
    media_group_kwargs = media_group_calls[0].full_kwargs
    assert media_group_kwargs["chat_id"] == 1900
    assert len(media_group_kwargs["media"]) == 2
    assert media_group_kwargs["media"][0].media == b"base64-string-1"
    assert media_group_kwargs["media"][1].media == b"base64-string-2"
    bot.method_calls.clear()

    # repeated call should use cached file ids
    set_return_for_send_photo(bot, ["file-id-1", "file-id-2"])
    await bot.process_new_updates([tg_update_message_to_bot(user_id=1900, first_name="User", text="/start")])
    assert len(bot.method_calls) == 1
    media_group_calls = bot.method_calls["send_media_group"]
    assert len(media_group_calls) == 1
    media_group_kwargs = media_group_calls[0].full_kwargs
    assert media_group_kwargs["chat_id"] == 1900
    assert len(media_group_kwargs["media"]) == 2
    assert media_group_kwargs["media"][0].media == "file-id-1"
    assert media_group_kwargs["media"][1].media == "file-id-2"
    bot.method_calls.clear()

    # modifying bot by adding one more file
    assert bot_config.user_flow_config.blocks[0].content is not None
    bot_config.user_flow_config.blocks[0].content.contents[0].attachments.append(
        ContentBlockContentAttachment(image=base64.b64encode(b"base64-string-3").decode())
    )
    bot_runner_2 = await construct_bot(
        username=username,
        bot_id="multiple-photos-in-content-block",
        bot_config=bot_config,
        form_results_store=dummy_form_results_store(),
        secret_store=secret_store,
        redis=redis,
        _bot_factory=MockedAsyncTeleBot,
    )
    bot_2 = bot_runner_2.bot
    assert isinstance(bot_2, MockedAsyncTeleBot)
    bot_2.method_calls.clear()

    # now first two files should be cached, but the third one not
    set_return_for_send_photo(bot_2, ["file-id-1", "file-id-2", "new-file-id"])
    await bot_2.process_new_updates([tg_update_message_to_bot(user_id=1900, first_name="User", text="/start")])
    assert len(bot_2.method_calls) == 1
    media_group_calls = bot_2.method_calls["send_media_group"]
    assert len(media_group_calls) == 1
    media_group_kwargs = media_group_calls[0].full_kwargs
    assert media_group_kwargs["chat_id"] == 1900
    assert len(media_group_kwargs["media"]) == 3
    assert media_group_kwargs["media"][0].media == "file-id-1"
    assert media_group_kwargs["media"][1].media == "file-id-2"
    assert media_group_kwargs["media"][2].media == b"base64-string-3"
    bot_2.method_calls.clear()

    # finally, all 3 files are cached
    set_return_for_send_photo(bot_2, ["file-id-1", "file-id-2", "new-file-id"])
    await bot_2.process_new_updates([tg_update_message_to_bot(user_id=1900, first_name="User", text="/start")])
    assert len(bot_2.method_calls) == 1
    media_group_calls = bot_2.method_calls["send_media_group"]
    assert len(media_group_calls) == 1
    media_group_kwargs = media_group_calls[0].full_kwargs
    assert media_group_kwargs["chat_id"] == 1900
    assert len(media_group_kwargs["media"]) == 3
    assert media_group_kwargs["media"][0].media == "file-id-1"
    assert media_group_kwargs["media"][1].media == "file-id-2"
    assert media_group_kwargs["media"][2].media == "new-file-id"
    bot_2.method_calls.clear()


def test_content_block_separates_too_long_caption() -> None:
    block = ContentBlock(
        block_id="content",
        contents=[
            Content(
                text=ContentText(
                    text="this caption is too long " * 100,
                    markup=ContentTextMarkup.HTML,
                ),
                attachments=[
                    ContentBlockContentAttachment(image=base64.b64encode(b"stuff").decode()),
                ],
            )
        ],
        next_block_id=None,
    )

    assert len(block.contents) == 2
    text_content = block.contents[0]
    assert not text_content.attachments
    assert text_content.text is not None
    assert text_content.text.text == "this caption is too long " * 100
    img_content = block.contents[1]
    assert img_content.text is None
    assert len(img_content.attachments) == 1


def test_content_block_splits_too_many_attachments() -> None:
    block = ContentBlock(
        block_id="content",
        contents=[
            Content(
                text=ContentText(
                    text="this caption is too long " * 100,
                    markup=ContentTextMarkup.HTML,
                ),
                attachments=[ContentBlockContentAttachment(image=f"stuff-{idx}") for idx in range(15)],
            )
        ],
        next_block_id=None,
    )

    assert len(block.contents) == 3
    text_content = block.contents[0]
    assert not text_content.attachments
    assert text_content.text is not None
    assert text_content.text.text == "this caption is too long " * 100

    img_content_1 = block.contents[1]
    assert img_content_1.text is None
    assert len(img_content_1.attachments) == 10

    img_content_2 = block.contents[2]
    assert img_content_2.text is None
    assert len(img_content_2.attachments) == 5
