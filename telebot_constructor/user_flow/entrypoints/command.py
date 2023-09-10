from typing import Optional
from telebot import types as tg

from telebot_constructor.user_flow.entrypoints.base import UserFlowEntryPoint
from telebot_constructor.user_flow.types import (
    EnterUserFlowBlockCallback,
    UserFlowBlockId,
    UserFlowContext,
    UserFlowSetupContext,
)


class CommandEntryPoint(UserFlowEntryPoint):
    command: str  # without leading slash, e.g. "start" instead of "/start"
    next_block_id: Optional[UserFlowBlockId]

    async def setup(self, context: UserFlowSetupContext, enter_block: EnterUserFlowBlockCallback) -> None:
        @context.bot.message_handler(commands=[self.command])
        async def cmd_handler(message: tg.Message) -> None:
            if self.next_block_id is not None:
                await enter_block(
                    self.next_block_id,
                    UserFlowContext(
                        bot=context.bot,
                        chat=message.chat,
                        user=message.from_user,
                        last_update_content=message,
                    ),
                )
