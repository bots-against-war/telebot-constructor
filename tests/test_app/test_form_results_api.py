from typing import Tuple

import aiohttp.web
from pytest_aiohttp.plugin import AiohttpClient  # type: ignore
from telebot import types as tg
from telebot.test_util import MockedAsyncTeleBot

from telebot_constructor.app import TelebotConstructorApp
from tests.test_app.conftest import MockBotRunner
from tests.utils import (
    RECENT_TIMESTAMP,
    mask_recent_timestamps,
    tg_update_message_to_bot,
)


async def test_form_results_api(
    constructor_app: Tuple[TelebotConstructorApp, aiohttp.web.Application],
    aiohttp_client: AiohttpClient,
) -> None:
    constructor, web_app = constructor_app
    client = await aiohttp_client(web_app)

    # saving a token
    resp = await client.post("/api/secrets/test-token", data="aaaaaa")
    assert resp.status == 200

    # saving a bot config
    resp = await client.post(
        "/api/config/mybot",
        json={
            "config": {
                "token_secret_name": "test-token",
                "user_flow_config": {
                    "entrypoints": [
                        {
                            "command": {
                                "entrypoint_id": "default-start-command",
                                "command": "start",
                                "next_block_id": "form-block-123",
                            },
                        }
                    ],
                    "blocks": [
                        {
                            "form": {
                                "block_id": "form-block-123",
                                "form_name": "super-form-testing-1-2",
                                "members": [
                                    {
                                        "field": {
                                            "plain_text": {
                                                "id": "form-field-1",
                                                "name": "one",
                                                "prompt": "Please answer the first question",
                                                "is_required": True,
                                                "result_formatting": "auto",
                                                "is_long_text": False,
                                                "empty_text_error_msg": "Error: empty answer",
                                            },
                                        },
                                    },
                                    {
                                        "field": {
                                            "plain_text": {
                                                "id": "form-field-2",
                                                "name": "two",
                                                "prompt": "Please answer the second question",
                                                "is_required": True,
                                                "result_formatting": "auto",
                                                "is_long_text": False,
                                                "empty_text_error_msg": "Error: empty answer",
                                            },
                                        },
                                    },
                                ],
                                "messages": {
                                    "form_start": "Hello welcome to the form testing bot",
                                    "cancel_command_is": "/cancel — to cancel",
                                    "field_is_skippable": "/skip — to skip",
                                    "field_is_not_skippable": "Field isn't skippable",
                                    "please_enter_correct_value": "Fix the value pls",
                                    "unsupported_command": "Bad cmd, get out",
                                },
                                "results_export": {
                                    "user_attribution": "name",
                                    "echo_to_user": True,
                                    "to_chat": None,
                                    "to_store": True,
                                },
                                "form_completed_next_block_id": None,
                                "form_cancelled_next_block_id": None,
                            },
                        },
                    ],
                    "node_display_coords": {},
                },
            },
            "display_name": "my test bot",
            "start": True,
            "version_message": "init",
        },
    )
    assert resp.status == 201

    resp = await client.get("/api/info/mybot")
    assert resp.status == 200
    print(await resp.json())
    assert mask_recent_timestamps(await resp.json()) == {
        "bot_name": "mybot",
        "display_name": "my test bot",
        "running_version": 0,
        "last_versions": [
            {
                "version": 0,
                "metadata": {
                    "timestamp": RECENT_TIMESTAMP,
                    "message": "init",
                },
            }
        ],
        "last_events": [
            {"timestamp": RECENT_TIMESTAMP, "username": "no-auth", "event": "edited", "new_version": 0},
            {"timestamp": RECENT_TIMESTAMP, "username": "no-auth", "event": "started", "version": 0},
        ],
        "forms_with_responses": [],
    }

    # assert isinstance(constructor.runner, MockBotRunner)
    # bot_runner = constructor.runner.running["no-auth"]["my-test-bot"]
    # assert isinstance(bot_runner.bot, MockedAsyncTeleBot)
    # await bot_runner.bot.process_new_updates(
    #     [
    #         tg_update_message_to_bot(
    #             user_id=123,
    #             first_name="User",
    #             text="/discover_chat",
    #             group_chat_id=456,
    #         )
    #     ]
    # )

    # resp = await client.post("/api/stop-group-chat-discovery/my-test-bot")
    # assert resp.status == 200

    # bot_runner.bot.add_return_values("get_chat", tg.Chat(id=456, type="supergroup", title="some group chat"))
    # resp = await client.get("/api/available-group-chats/my-test-bot")
    # assert resp.status == 200
    # assert await resp.json() == [
    #     {
    #         "id": 456,
    #         "type": "supergroup",
    #         "title": "some group chat",
    #         "description": None,
    #         "username": None,
    #         "is_forum": None,
    #         "photo": None,
    #     }
    # ]
