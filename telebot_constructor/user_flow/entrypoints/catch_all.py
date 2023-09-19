from typing import Optional

from telebot import types as tg

from telebot_constructor.user_flow.entrypoints.base import UserFlowEntryPoint
from telebot_constructor.user_flow.types import (
    SetupResult,
    UserFlowBlockId,
    UserFlowContext,
    UserFlowSetupContext,
)


class CatchAllEntryPoint(UserFlowEntryPoint):
    """Entry point that catches all user messages"""

    next_block_id: Optional[UserFlowBlockId]

    async def setup(self, context: UserFlowSetupContext) -> SetupResult:
        # NOTE: lowest priority to not interfere with more specific handlers
        @context.bot.message_handler(priority=-1000)
        async def catch_all_handler(message: tg.Message) -> None:
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

    def is_catch_all(self) -> bool:
        return True
