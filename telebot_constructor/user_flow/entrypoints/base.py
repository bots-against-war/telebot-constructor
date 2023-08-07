import abc

from pydantic import BaseModel

from telebot_constructor.user_flow.types import (
    EnterUserFlowBlockCallback,
    UserFlowSetupContext,
)


class UserFlowEntryPoint(BaseModel, abc.ABC):
    """User flow component that is responsible for starting the flow"""

    @abc.abstractmethod
    async def setup(self, context: UserFlowSetupContext, enter_block: EnterUserFlowBlockCallback) -> None:
        ...
