from typing import Optional

from telebot import types as tg

from telebot_constructor.user_flow.entrypoints.base import UserFlowEntryPoint
from telebot_constructor.user_flow.types import (
    SetupResult,
    UserFlowBlockId,
    UserFlowContext,
    UserFlowSetupContext,
)
from telebot_constructor.utils import without_nones


class CatchAllEntryPoint(UserFlowEntryPoint):
    """Entrypoint that catches all user messages"""

    next_block_id: Optional[UserFlowBlockId]

    async def setup(self, context: UserFlowSetupContext) -> SetupResult:
        # NOTE: lowest priority to not interfere with more specific handlers
        @context.bot.message_handler(priority=-1000, func=context.banned_users_store.not_from_banned_user)
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

    def possible_next_block_ids(self) -> list[str]:
        return without_nones([self.next_block_id])
