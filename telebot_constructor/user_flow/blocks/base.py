import abc

from pydantic import BaseModel

from telebot_constructor.user_flow.types import (
    EnterUserFlowBlockCallback,
    UserFlowBlockId,
    UserFlowContext,
    UserFlowSetupContext,
)


class UserFlowBlock(BaseModel, abc.ABC):
    """Single block in the user flow representing a particular state of user-bot interaction"""

    block_id: UserFlowBlockId  # mandatory field for all blocks; id by which they can be referenced in the flow

    @abc.abstractmethod
    async def enter(self, context: UserFlowContext, enter_block: EnterUserFlowBlockCallback) -> None:
        """
        Enter the block within the context.

        This method may be invoked by
        - an entry point (e.g. /command), when starting the flow
        - another block, when going through the flow

        The method can use the passed user flow enter_block to invoke other blocks.
        """
        ...

    @abc.abstractmethod
    async def setup(self, context: UserFlowSetupContext, enter_block: EnterUserFlowBlockCallback) -> None:
        """
        Setup handlers necessary for the block to work. Invoked once when constucting the bot.
        """
        ...
