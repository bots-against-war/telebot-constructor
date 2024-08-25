import copy
from typing import Optional

from pydantic import BaseModel, model_validator

from telebot_constructor.user_flow import UserFlow
from telebot_constructor.user_flow.blocks.base import UserFlowBlock
from telebot_constructor.user_flow.blocks.content import ContentBlock
from telebot_constructor.user_flow.blocks.form import FormBlock
from telebot_constructor.user_flow.blocks.human_operator import HumanOperatorBlock
from telebot_constructor.user_flow.blocks.internal import BotErrorBlock
from telebot_constructor.user_flow.blocks.language_select import LanguageSelectBlock
from telebot_constructor.user_flow.blocks.menu import MenuBlock
from telebot_constructor.user_flow.entrypoints.base import UserFlowEntryPoint
from telebot_constructor.user_flow.entrypoints.catch_all import CatchAllEntryPoint
from telebot_constructor.user_flow.entrypoints.command import CommandEntryPoint
from telebot_constructor.user_flow.entrypoints.regex_match import RegexMatchEntryPoint
from telebot_constructor.utils.pydantic import ExactlyOneNonNullFieldModel


class UserFlowEntryPointConfig(ExactlyOneNonNullFieldModel):
    command: Optional[CommandEntryPoint] = None
    catch_all: Optional[CatchAllEntryPoint] = None
    regex: Optional[RegexMatchEntryPoint] = None

    def to_user_flow_entrypoint(self) -> UserFlowEntryPoint:
        # runtime guarantee that exactly one of the options is not None
        return copy.deepcopy(self.command or self.catch_all or self.regex)  # type: ignore


class UserFlowBlockConfig(ExactlyOneNonNullFieldModel):
    content: Optional[ContentBlock] = None
    human_operator: Optional[HumanOperatorBlock] = None
    menu: Optional[MenuBlock] = None
    form: Optional[FormBlock] = None
    language_select: Optional[LanguageSelectBlock] = None

    # internal block types, used for debugging and tests
    error: Optional[BotErrorBlock] = None

    def to_user_flow_block(self) -> UserFlowBlock:
        block = copy.deepcopy(
            self.content or self.human_operator or self.menu or self.form or self.language_select or self.error,
        )
        # runtime guarantee that exactly one of the options is not None
        assert block is not None, "failed to extract user flow block config, did someone forgot to add it to or-chain?"
        return block


class UserFlowNodePosition(BaseModel):
    x: float
    y: float


class UserFlowConfig(BaseModel):
    entrypoints: list[UserFlowEntryPointConfig]
    blocks: list[UserFlowBlockConfig]

    # entrypoint/block id -> display position on frontend
    # not used for bot logic, but still stored
    node_display_coords: dict[str, UserFlowNodePosition]

    @model_validator(mode="after")
    def config_convertible_to_user_flow(self) -> "UserFlowConfig":
        self.to_user_flow()
        return self

    def to_user_flow(self) -> UserFlow:
        return UserFlow(
            entrypoints=[entrypoint_config.to_user_flow_entrypoint() for entrypoint_config in self.entrypoints],
            blocks=[block_config.to_user_flow_block() for block_config in self.blocks],
        )


class BotConfig(BaseModel):
    token_secret_name: str  # must correspond to a valid secret in secret store
    user_flow_config: UserFlowConfig

    display_name: Optional[str] = None

    def stub(self) -> "BotConfig":
        """Stub bots are run with a barebones config; it is not saved to DB and is never shown to the user"""
        return BotConfig(
            token_secret_name=self.token_secret_name,
            user_flow_config=UserFlowConfig(entrypoints=[], blocks=[], node_display_coords={}),
        )
