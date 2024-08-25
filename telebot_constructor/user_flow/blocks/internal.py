"""
Internal blocks that are useful for testing
"""

import logging

from telebot_constructor.user_flow.blocks.base import UserFlowBlock
from telebot_constructor.user_flow.types import (
    SetupResult,
    UserFlowContext,
    UserFlowSetupContext,
)

logger = logging.getLogger(__name__)


class BotErrorBlock(UserFlowBlock):
    """
    User flow block that raises an exception when the user enters it.
    """

    def possible_next_block_ids(self) -> list[str]:
        return []

    async def enter(self, context: UserFlowContext) -> None:
        raise RuntimeError(f"User entered the error block ({self.block_id=!r})")

    async def setup(self, context: UserFlowSetupContext) -> SetupResult:
        return SetupResult.empty()
