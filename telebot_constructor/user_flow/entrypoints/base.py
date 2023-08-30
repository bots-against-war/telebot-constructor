import abc

from pydantic import BaseModel

from telebot_constructor.user_flow.types import (
    EnterUserFlowBlockCallback,
    UserFlowSetupContext,
)


class UserFlowEntryPoint(BaseModel, abc.ABC):
    """User flow component responsible for initiating the flow"""

    entrypoint_id: str

    @abc.abstractmethod
    async def setup(self, context: UserFlowSetupContext, enter_block: EnterUserFlowBlockCallback) -> None:
        ...
