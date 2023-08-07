from dataclasses import dataclass
from typing import Optional

from telebot import types as tg

from telebot_constructor.user_flow.blocks.base import UserFlowBlock
from telebot_constructor.user_flow.types import (
    EnterUserFlowBlockCallback,
    UserFlowBlockId,
    UserFlowContext,
    UserFlowSetupContext,
)


@dataclass
class MessageBlock(UserFlowBlock):
    """Simplest user flow block: send message and immediately continue to the next block"""

    message_text: str  # TODO: attachments and other good stuff
    next_block_id: Optional[UserFlowBlockId]

    async def enter(self, context: UserFlowContext, enter_block: EnterUserFlowBlockCallback) -> None:
        await context.bot.send_message(context.user.id, self.message_text, reply_markup=tg.ReplyKeyboardRemove())
        if self.next_block_id is not None:
            await enter_block(self.next_block_id, context)

    async def setup(self, context: UserFlowSetupContext, enter_block: EnterUserFlowBlockCallback) -> None:
        pass  # nothing to setup here
