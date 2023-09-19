from typing import Optional

from telebot import types as tg

from telebot_constructor.user_flow.entrypoints.base import UserFlowEntryPoint
from telebot_constructor.user_flow.types import (
    SetupResult,
    UserFlowBlockId,
    UserFlowContext,
    UserFlowSetupContext,
)


class CommandEntryPoint(UserFlowEntryPoint):
    """Basic entry-point catching Telegram /commands"""
    command: str  # without leading slash, e.g. "start" instead of "/start"
    next_block_id: Optional[UserFlowBlockId]
    short_description: Optional[str] = None  # used for native Telegram menu

    async def setup(self, context: UserFlowSetupContext) -> SetupResult:
        @context.bot.message_handler(commands=[self.command])
        async def cmd_handler(message: tg.Message) -> None:
            if self.next_block_id is not None:
                await context.enter_block(
                    self.next_block_id,
                    UserFlowContext.from_setup_context(
                        setup_ctx=context,
                        chat=message.chat,
                        user=message.from_user,
                        last_update_content=message,
                    ),
                )

        return SetupResult.empty()
