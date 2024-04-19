import abc

from pydantic import BaseModel

from telebot_constructor.user_flow.types import SetupResult, UserFlowSetupContext


class UserFlowEntryPoint(BaseModel, abc.ABC):
    """User flow component responsible for initiating the flow"""

    entrypoint_id: str

    def __str__(self) -> str:
        return f'Entrypoint "{self.entrypoint_id}" ({self.__class__.__name__})'

    @abc.abstractmethod
    async def setup(self, context: UserFlowSetupContext) -> SetupResult: ...

    def is_catch_all(self) -> bool:
        return False

    @abc.abstractmethod
    def possible_next_block_ids(self) -> list[str]: ...
