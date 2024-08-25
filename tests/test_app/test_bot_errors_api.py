import time
from typing import Tuple

import aiohttp.web
from pytest_aiohttp.plugin import AiohttpClient  # type: ignore
from telebot.metrics import TelegramUpdateMetrics
from telebot.test_util import MockedAsyncTeleBot

from telebot_constructor.app import TelebotConstructorApp
from tests.test_app.conftest import MockBotRunner
from tests.utils import (
    RECENT_TIMESTAMP,
    SMALL_TIME_DURATION,
    mask_recent_timestamps,
    mask_small_time_durations,
    tg_update_message_to_bot,
)


async def test_bot_errors_api(
    constructor_app: Tuple[TelebotConstructorApp, aiohttp.web.Application],
    aiohttp_client: AiohttpClient,
) -> None:
    constructor, web_app = constructor_app
    client = await aiohttp_client(web_app)

    # saving a token
    resp = await client.post("/api/secrets/test-token", data="hello")
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
                                "entrypoint_id": "start",
                                "command": "start",
                                "next_block_id": "error-block",
                            },
                        }
                    ],
                    "blocks": [{"error": {"block_id": "error-block"}}],
                    "node_display_coords": {},
                },
            },
            "display_name": "my test bot",
            "start": True,
            "version_message": "init",
        },
    )
    assert resp.status == 201

    # users are interacting with bot and triggering errors
    assert isinstance(constructor.runner, MockBotRunner)
    bot_runner = constructor.runner.running["no-auth"]["mybot"]
    assert isinstance(bot_runner.bot, MockedAsyncTeleBot)
    bot = bot_runner.bot
    assert isinstance(bot, MockedAsyncTeleBot)
    bot.method_calls.clear()
    await bot.process_new_updates(
        [
            tg_update_message_to_bot(
                user_id=user_id,
                first_name="john pork",
                text="/start",
                metrics=TelegramUpdateMetrics(bot_prefix="test-bot", received_at=time.time()),
            )
            for user_id in range(30)
        ]
    )
    assert not bot.method_calls

    # TODO: checking bot info, the last error should be there
    resp = await client.get("/api/info/mybot")
    assert resp.status == 200
    assert mask_small_time_durations(mask_recent_timestamps(await resp.json())) == {
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
        "last_errors": [
            {
                "timestamp": RECENT_TIMESTAMP,
                "update_metrics": {
                    "bot_prefix": "test-bot",
                    "exception_info": {
                        "body": "User entered the error block (self.block_id='error-block')",
                        "type_name": "RuntimeError",
                    },
                    "handler_name": (
                        "telebot_constructor.user_flow.entrypoints.command."
                        "CommandEntryPoint.setup.<locals>.cmd_handler"
                    ),
                    "handler_test_durations": [SMALL_TIME_DURATION],
                    "processing_duration": SMALL_TIME_DURATION,
                    "received_at": RECENT_TIMESTAMP,
                },
            }
            for _ in range(10)
        ],
    }

    # calling the bot errors api to get the full list
    resp = await client.get("/api/errors/mybot")
    assert resp.status == 200
    assert mask_small_time_durations(mask_recent_timestamps(await resp.json())) == {
        "errors": [
            # NOTE: due to a hacky details of update parsing and metrics initialization these test
            # examples lack some info contained in real world metrics, but this is not the point of
            # this test anyway
            {
                "timestamp": RECENT_TIMESTAMP,
                "update_metrics": {
                    "bot_prefix": "test-bot",
                    "exception_info": {
                        "body": "User entered the error block (self.block_id='error-block')",
                        "type_name": "RuntimeError",
                    },
                    "handler_name": (
                        "telebot_constructor.user_flow.entrypoints.command."
                        "CommandEntryPoint.setup.<locals>.cmd_handler"
                    ),
                    "handler_test_durations": [SMALL_TIME_DURATION],
                    "processing_duration": SMALL_TIME_DURATION,
                    "received_at": RECENT_TIMESTAMP,
                },
            }
            for _ in range(20)
        ],
    }
