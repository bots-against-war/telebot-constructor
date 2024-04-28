from typing import Any

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
from telebot_constructor.user_flow.blocks.content import ContentBlock
from telebot_constructor.user_flow.blocks.form import (
    BranchingFormMemberConfig,
    EnumOption,
    FormBlock,
    FormBranchConfig,
    FormFieldConfig,
    FormMessages,
    FormResultsExport,
    FormResultsExportToChatConfig,
    FormResultUserAttribution,
    PlainTextFormFieldConfig,
    SingleSelectFormFieldConfig,
)
from telebot_constructor.user_flow.entrypoints.command import CommandEntryPoint
from tests.utils import (
    assert_method_call_dictified_kwargs_include,
    assert_method_call_kwargs_include,
    dummy_form_results_store,
    dummy_secret_store,
    tg_update_message_to_bot,
)


@pytest.mark.parametrize(
    "form_result_export_kwargs, expected_name_line",
    [
        pytest.param(
            dict(is_anonymous=False),
            '<a href="tg://user?id=161">User</a>\n\n',
            id="legacy way of specifying user attribution by flag = true",
        ),
        pytest.param(
            dict(is_anonymous=True),
            "",
            id="legacy way of specifying user attribution by flag = false",
        ),
        pytest.param(
            dict(user_attribution=FormResultUserAttribution.FULL),
            '<a href="tg://user?id=161">User</a>\n\n',
            id="full user attribution",
        ),
        pytest.param(
            dict(user_attribution=FormResultUserAttribution.NAME),
            "User\n\n",
            id="name-only user attribution",
        ),
        pytest.param(
            dict(user_attribution=FormResultUserAttribution.UNIQUE_ID),
            "🤯🧄🌝🎳🚿♿\n\n",
            id="anonymized id user attribution",
        ),
        pytest.param(
            dict(user_attribution=FormResultUserAttribution.NONE),
            "",
            id="no user attribution",
        ),
    ],
)
async def test_user_flow_with_form(
    form_result_export_kwargs: dict[str, Any],
    expected_name_line: str,
) -> None:
    bot_config = BotConfig(
        token_secret_name="token",
        display_name="lalala",
        user_flow_config=UserFlowConfig(
            entrypoints=[
                UserFlowEntryPointConfig(
                    command=CommandEntryPoint(
                        entrypoint_id="start-cmd",
                        command="start",
                        next_block_id="hello-msg",
                    ),
                ),
            ],
            blocks=[
                UserFlowBlockConfig(
                    content=ContentBlock.simple_text(
                        block_id="hello-msg",
                        message_text="hi i'm form bot",
                        next_block_id="form",
                    ),
                ),
                UserFlowBlockConfig(
                    content=ContentBlock.simple_text(
                        block_id="thanks-msg",
                        message_text="thanks for using the bot",
                        next_block_id=None,
                    ),
                ),
                UserFlowBlockConfig(
                    form=FormBlock(
                        block_id="form",
                        form_name="test-form",
                        members=[
                            BranchingFormMemberConfig(
                                field=FormFieldConfig(
                                    plain_text=PlainTextFormFieldConfig(
                                        id="name",
                                        name="Name",
                                        prompt="what is your name?",
                                        is_long_text=False,
                                        is_required=True,
                                        result_formatting="auto",
                                        empty_text_error_msg="please provide an answer",
                                    ),
                                )
                            ),
                            BranchingFormMemberConfig(
                                field=FormFieldConfig(
                                    single_select=SingleSelectFormFieldConfig(
                                        id="does_like_apples",
                                        name="Apples",
                                        prompt="do you like apples?",
                                        is_required=True,
                                        result_formatting="auto",
                                        options=[
                                            EnumOption(id="yes", label="Yes I do"),
                                            EnumOption(id="no", label="No!!!"),
                                        ],
                                        invalid_enum_error_msg="please use reply keyboard buttons",
                                    ),
                                )
                            ),
                            BranchingFormMemberConfig(
                                branch=FormBranchConfig(
                                    members=[
                                        BranchingFormMemberConfig(
                                            field=FormFieldConfig(
                                                plain_text=PlainTextFormFieldConfig(
                                                    id="which_apples",
                                                    name="Which apples",
                                                    prompt="which apples do you like?",
                                                    is_required=True,
                                                    is_long_text=False,
                                                    result_formatting="auto",
                                                    empty_text_error_msg="please answer the question",
                                                )
                                            )
                                        )
                                    ],
                                    condition_match_value="yes",
                                )
                            ),
                        ],
                        messages=FormMessages(
                            form_start="hi please fill out the form!",
                            cancel_command_is="{} - cancel filling",
                            field_is_skippable="skip field - {}",
                            field_is_not_skippable="field is not skippable",
                            please_enter_correct_value="please enter corrected value",
                            unsupported_command="the only supported commands are: {}",
                        ),
                        results_export=FormResultsExport(
                            echo_to_user=True,
                            to_chat=FormResultsExportToChatConfig(chat_id=111222, via_feedback_handler=True),
                            **form_result_export_kwargs,
                        ),
                        form_completed_next_block_id="thanks-msg",
                        form_cancelled_next_block_id=None,
                    ),
                ),
            ],
            node_display_coords={},
        ),
    )
    redis = RedisEmulation()
    secret_store = dummy_secret_store(redis)
    username = "bot-admin-1312"
    await secret_store.save_secret(secret_name="token", secret_value="mock-token", owner_id=username)
    bot_runner = await construct_bot(
        username=username,
        bot_name="form-bot-test",
        bot_config=bot_config,
        form_results_store=dummy_form_results_store(),
        secret_store=secret_store,
        redis=redis,
        _bot_factory=MockedAsyncTeleBot,
    )
    assert not bot_runner.background_jobs
    assert not bot_runner.aux_endpoints

    bot = bot_runner.bot
    assert isinstance(bot, MockedAsyncTeleBot)
    bot.method_calls.clear()

    # using start command to start the form
    await bot.process_new_updates([tg_update_message_to_bot(161, first_name="User", text="/start")])
    assert len(bot.method_calls) == 1
    assert_method_call_kwargs_include(
        bot.method_calls["send_message"],
        [
            {"text": "hi i'm form bot", "chat_id": 161},
            {"chat_id": 161, "text": "hi please fill out the form!\n\n/cancel - cancel filling"},
            {"chat_id": 161, "text": "what is your name?"},
        ],
    )
    assert_method_call_dictified_kwargs_include(bot.method_calls["send_message"], [{}, {}, {}])
    bot.method_calls.clear()

    await bot.process_new_updates([tg_update_message_to_bot(161, first_name="User", text="John Doe")])
    assert len(bot.method_calls) == 1
    assert_method_call_kwargs_include(
        bot.method_calls["send_message"],
        [
            {"chat_id": 161, "text": "do you like apples?"},
        ],
    )
    assert_method_call_dictified_kwargs_include(
        bot.method_calls["send_message"],
        [
            {
                "reply_markup": {
                    "keyboard": [[{"text": "Yes I do"}, {"text": "No!!!"}]],
                    "one_time_keyboard": True,
                    "resize_keyboard": True,
                },
            }
        ],
    )
    bot.method_calls.clear()

    await bot.process_new_updates([tg_update_message_to_bot(161, first_name="User", text="Yes I do")])
    assert len(bot.method_calls) == 1
    assert_method_call_kwargs_include(
        bot.method_calls["send_message"],
        [
            {"chat_id": 161, "text": "which apples do you like?"},
        ],
    )
    bot.method_calls.clear()

    await bot.process_new_updates([tg_update_message_to_bot(161, first_name="User", text="granny smith")])
    assert len(bot.method_calls) == 1
    assert_method_call_kwargs_include(
        bot.method_calls["send_message"],
        [
            {
                "chat_id": 161,
                "text": ("<b>Name</b>: John Doe\n" + "<b>Apples</b>: Yes I do\n" + "<b>Which apples</b>: granny smith"),
                "parse_mode": "HTML",
            },
            {
                "chat_id": 111222,
                "text": (
                    expected_name_line
                    + "<b>Name</b>: John Doe\n"
                    + "<b>Apples</b>: Yes I do\n"
                    + "<b>Which apples</b>: granny smith"
                ),
                "parse_mode": "HTML",
            },
            {"text": "thanks for using the bot", "chat_id": 161},
        ],
    )
    bot.method_calls.clear()
