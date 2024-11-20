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
from telebot_constructor.user_flow.blocks.menu import (
    Menu,
    MenuBlock,
    MenuConfig,
    MenuItem,
    MenuMechanism,
)
from telebot_constructor.user_flow.entrypoints.command import CommandEntryPoint
from tests.utils import (
    assert_method_call_dictified_kwargs_include,
    dummy_form_results_store,
    dummy_metrics_store,
    dummy_secret_store,
    tg_update_callback_query,
    tg_update_message_to_bot,
)


def make_menu_blocks(connections: dict[str, list[str]]) -> list[MenuBlock]:
    return [
        MenuBlock(
            block_id=f"menu-{menu_name}",
            menu=Menu(
                text=menu_name,
                items=[
                    MenuItem(
                        label=submenu_name,
                        next_block_id=f"menu-{submenu_name}",
                    )
                    for submenu_name in next_block_ids
                ],
                config=MenuConfig(
                    back_label="<-",
                    lock_after_termination=False,
                    mechanism=MenuMechanism.INLINE_BUTTONS,
                ),
            ),
        )
        for menu_name, next_block_ids in connections.items()
    ]


async def test_multilevel_menu() -> None:
    """
    A multilevel menu that is traversible back and forth
    ┌───┐
    │ A │
    └─┬─┘
      │
    ┌─▼─┐
    │ B │
    └─┬─┘
      │
    ┌─▼─┐
    │ C │
    └───┘
    """
    USER_ID = 1312

    menu_a, menu_b, menu_c = make_menu_blocks({"A": ["B"], "B": ["C"], "C": []})
    menu_c.menu.items.append(MenuItem(label="finish", next_block_id="fin-message"))
    bot_config = BotConfig(
        token_secret_name="token",
        display_name="Menu bot",
        user_flow_config=UserFlowConfig(
            entrypoints=[
                UserFlowEntryPointConfig(
                    command=CommandEntryPoint(entrypoint_id="start-cmd", command="start", next_block_id="menu-A"),
                )
            ],
            blocks=[
                UserFlowBlockConfig(menu=menu_a),
                UserFlowBlockConfig(menu=menu_b),
                UserFlowBlockConfig(menu=menu_c),
                UserFlowBlockConfig(
                    content=ContentBlock.simple_text(block_id="fin-message", message_text="finish", next_block_id=None),
                ),
            ],
            node_display_coords={},
        ),
    )

    redis = RedisEmulation()
    secret_store = dummy_secret_store(redis)
    username = "user12345"
    await secret_store.save_secret(secret_name="token", secret_value="mock-token", owner_id=username)
    bot_runner = await construct_bot(
        username=username,
        bot_id="menu-bot",
        bot_config=bot_config,
        form_results_store=dummy_form_results_store(),
        metrics_store=dummy_metrics_store(),
        secret_store=secret_store,
        redis=redis,
        _bot_factory=MockedAsyncTeleBot,
    )

    assert not bot_runner.background_jobs
    assert not bot_runner.aux_endpoints

    bot = bot_runner.bot
    assert isinstance(bot, MockedAsyncTeleBot)
    bot.method_calls.clear()

    # /start command
    await bot.process_new_updates([tg_update_message_to_bot(USER_ID, first_name="User", text="/start")])
    assert_method_call_dictified_kwargs_include(
        bot.method_calls["send_message"],
        [
            {
                "chat_id": USER_ID,
                "text": "A",
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "B", "callback_data": "menu:3b7f5e8a6401a0e6-1"}],
                    ]
                },
            }
        ],
    )
    bot.method_calls.clear()

    # to the next menu
    await bot.process_new_updates(
        [tg_update_callback_query(USER_ID, first_name="User", callback_query="menu:3b7f5e8a6401a0e6-1")]
    )
    assert_method_call_dictified_kwargs_include(
        bot.method_calls["edit_message_text"],
        [
            {
                "message_id": 1,
                "chat_id": 1312,
                "text": "B",
                "parse_mode": None,
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "C", "callback_data": "menu:3b7f5e8a6401a0e6-2"}],
                        [{"text": "<-", "callback_data": "menu:3b7f5e8a6401a0e6-0"}],
                    ]
                },
            }
        ],
    )
    bot.method_calls.clear()

    # ...and to the next
    await bot.process_new_updates(
        [tg_update_callback_query(USER_ID, first_name="User", callback_query="menu:3b7f5e8a6401a0e6-2")]
    )
    assert_method_call_dictified_kwargs_include(
        bot.method_calls["edit_message_text"],
        [
            {
                "chat_id": 1312,
                "text": "C",
                "parse_mode": None,
                "message_id": 1,
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "finish", "callback_data": "terminator:3b7f5e8a6401a0e6-2"}],
                        [{"text": "<-", "callback_data": "menu:3b7f5e8a6401a0e6-1"}],
                    ]
                },
            }
        ],
    )
    bot.method_calls.clear()

    # back to B
    await bot.process_new_updates(
        [tg_update_callback_query(USER_ID, first_name="User", callback_query="menu:3b7f5e8a6401a0e6-1")]
    )
    assert_method_call_dictified_kwargs_include(
        bot.method_calls["edit_message_text"],
        [
            {
                "chat_id": 1312,
                "text": "B",
                "parse_mode": None,
                "message_id": 1,
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "C", "callback_data": "menu:3b7f5e8a6401a0e6-2"}],
                        [{"text": "<-", "callback_data": "menu:3b7f5e8a6401a0e6-0"}],
                    ]
                },
            }
        ],
    )
    bot.method_calls.clear()


async def test_dag_menu() -> None:
    """
    A menu with a DAG connection.

    The menu has two entry points: from A, in which case the "back" from E will lead to D because
    it's a shorter path from root; from B, in which case only B-C-E branch is accessible as a
    linear 2-level menu

        ┌───┐
      ┌─┤ A ├─┐
      │ └───┘ │
    ┌─▼─┐   ┌─▼─┐
    │ B │   │ D │
    └─┬─┘   └─┬─┘
    ┌─▼─┐   ┌─▼─┐
    │ C │──►│ E │
    └───┘   └───┘
    """
    USER_ID = 1312

    menu_blocks = make_menu_blocks({"A": ["B", "D"], "B": ["C"], "C": ["E"], "D": ["E"], "E": []})
    bot_config = BotConfig(
        token_secret_name="token",
        display_name="Menu bot",
        user_flow_config=UserFlowConfig(
            entrypoints=[
                UserFlowEntryPointConfig(
                    command=CommandEntryPoint(entrypoint_id="start-cmd", command="start", next_block_id="menu-A"),
                ),
                UserFlowEntryPointConfig(
                    command=CommandEntryPoint(entrypoint_id="aux-cmd", command="aux", next_block_id="menu-B"),
                ),
            ],
            blocks=[UserFlowBlockConfig(menu=menu) for menu in menu_blocks],
            node_display_coords={},
        ),
    )

    redis = RedisEmulation()
    secret_store = dummy_secret_store(redis)
    username = "user12345"
    await secret_store.save_secret(secret_name="token", secret_value="mock-token", owner_id=username)
    bot_runner = await construct_bot(
        username=username,
        bot_id="menu-bot",
        bot_config=bot_config,
        form_results_store=dummy_form_results_store(),
        metrics_store=dummy_metrics_store(),
        secret_store=secret_store,
        redis=redis,
        _bot_factory=MockedAsyncTeleBot,
    )

    assert not bot_runner.background_jobs
    assert not bot_runner.aux_endpoints

    bot = bot_runner.bot
    assert isinstance(bot, MockedAsyncTeleBot)
    bot.method_calls.clear()

    # entry point 1

    # /start command
    await bot.process_new_updates([tg_update_message_to_bot(USER_ID, first_name="User", text="/start")])
    assert_method_call_dictified_kwargs_include(
        bot.method_calls["send_message"],
        [
            {
                "text": "A",
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "B", "callback_data": "menu:3b7f5e8a6401a0e6-1"}],
                        [{"text": "D", "callback_data": "menu:3b7f5e8a6401a0e6-2"}],
                    ]
                },
            }
        ],
    )
    bot.method_calls.clear()

    # D -> E branch
    await bot.process_new_updates(
        [tg_update_callback_query(USER_ID, first_name="User", callback_query="menu:3b7f5e8a6401a0e6-2")]
    )
    assert_method_call_dictified_kwargs_include(
        bot.method_calls["edit_message_text"],
        [
            {
                "text": "D",
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "E", "callback_data": "menu:3b7f5e8a6401a0e6-4"}],
                        [{"text": "<-", "callback_data": "menu:3b7f5e8a6401a0e6-0"}],
                    ]
                },
            }
        ],
    )
    bot.method_calls.clear()

    await bot.process_new_updates(
        [tg_update_callback_query(USER_ID, first_name="User", callback_query="menu:3b7f5e8a6401a0e6-4")]
    )
    assert_method_call_dictified_kwargs_include(
        bot.method_calls["edit_message_text"],
        [
            {
                "text": "E",
                "reply_markup": {"inline_keyboard": [[{"text": "<-", "callback_data": "menu:3b7f5e8a6401a0e6-2"}]]},
            }
        ],
    )
    bot.method_calls.clear()

    # B -> C branch
    await bot.process_new_updates(
        [tg_update_callback_query(USER_ID, first_name="User", callback_query="menu:3b7f5e8a6401a0e6-1")]
    )
    assert_method_call_dictified_kwargs_include(
        bot.method_calls["edit_message_text"],
        [
            {
                "text": "B",
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "C", "callback_data": "menu:3b7f5e8a6401a0e6-3"}],
                        [{"text": "<-", "callback_data": "menu:3b7f5e8a6401a0e6-0"}],
                    ]
                },
            }
        ],
    )
    bot.method_calls.clear()

    await bot.process_new_updates(
        [tg_update_callback_query(USER_ID, first_name="User", callback_query="menu:3b7f5e8a6401a0e6-3")]
    )
    assert_method_call_dictified_kwargs_include(
        bot.method_calls["edit_message_text"],
        [
            {
                "chat_id": 1312,
                "text": "C",
                "parse_mode": None,
                "message_id": 1,
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "E", "callback_data": "terminator:3b7f5e8a6401a0e6-4"}],
                        [{"text": "<-", "callback_data": "menu:3b7f5e8a6401a0e6-1"}],
                    ]
                },
            }
        ],
    )
    bot.method_calls.clear()

    await bot.process_new_updates(
        [tg_update_callback_query(USER_ID, first_name="User", callback_query="terminator:3b7f5e8a6401a0e6-4")]
    )
    assert_method_call_dictified_kwargs_include(
        bot.method_calls["send_message"],
        [
            {"chat_id": 1312, "text": "E", "parse_mode": None, "reply_markup": {"inline_keyboard": []}},
        ],
    )
    bot.method_calls.clear()

    # entry point 2

    # /aux command
    await bot.process_new_updates([tg_update_message_to_bot(USER_ID, first_name="User", text="/aux")])
    assert_method_call_dictified_kwargs_include(
        bot.method_calls["send_message"],
        [
            {
                "text": "B",
                "reply_markup": {"inline_keyboard": [[{"text": "C", "callback_data": "menu:c5095a1b07406fc0-1"}]]},
            }
        ],
    )
    bot.method_calls.clear()

    await bot.process_new_updates(
        [tg_update_callback_query(USER_ID, first_name="User", callback_query="menu:c5095a1b07406fc0-1")]
    )
    assert_method_call_dictified_kwargs_include(
        bot.method_calls["edit_message_text"],
        [
            {
                "text": "C",
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "E", "callback_data": "menu:c5095a1b07406fc0-2"}],
                        [{"text": "<-", "callback_data": "menu:c5095a1b07406fc0-0"}],
                    ]
                },
            }
        ],
    )
    bot.method_calls.clear()

    await bot.process_new_updates(
        [tg_update_callback_query(USER_ID, first_name="User", callback_query="menu:c5095a1b07406fc0-2")]
    )
    assert_method_call_dictified_kwargs_include(
        bot.method_calls["edit_message_text"],
        [
            {
                "text": "E",
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "<-", "callback_data": "menu:c5095a1b07406fc0-1"}],
                    ]
                },
            }
        ],
    )
    bot.method_calls.clear()
