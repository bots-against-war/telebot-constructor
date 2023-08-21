from datetime import timedelta
from typing import Optional

from pydantic import BaseModel, model_validator
from telebot_components.constants import times

from telebot_constructor.pydantic_utils import ExactlyOneNonNullFieldModel
from telebot_constructor.user_flow import UserFlow
from telebot_constructor.user_flow.blocks.base import UserFlowBlock
from telebot_constructor.user_flow.blocks.message import MessageBlock
from telebot_constructor.user_flow.entrypoints.base import UserFlowEntryPoint
from telebot_constructor.user_flow.entrypoints.command import CommandEntryPoint


class UserFlowEntryPointConfig(ExactlyOneNonNullFieldModel):
    command: Optional[CommandEntryPoint]

    def to_user_flow_entrypoint(self) -> UserFlowEntryPoint:
        # runtime guarantee that exactly one of the options is not None
        return self.command  # type: ignore


class UserFlowBlockConfig(ExactlyOneNonNullFieldModel):
    message: Optional[MessageBlock]

    def to_user_flow_block(self) -> UserFlowBlock:
        # runtime guarantee that exactly one of the options is not None
        return self.message  # type: ignore


class UserFlowConfig(BaseModel):
    entrypoints: list[UserFlowEntryPointConfig]
    blocks: list[UserFlowBlockConfig]

    @model_validator(mode="after")
    def config_convertible_to_user_flow(self) -> "UserFlowConfig":
        self.to_user_flow()
        return self

    def to_user_flow(self) -> UserFlow:
        return UserFlow(
            entrypoints=[entrypoint_config.to_user_flow_entrypoint() for entrypoint_config in self.entrypoints],
            blocks=[block_config.to_user_flow_block() for block_config in self.blocks],
        )


class FeedbackHandlerConfig(BaseModel):
    admin_chat_id: int
    message_log_to_admin_chat: bool = True
    force_category_selection: bool = False
    hashtags_in_admin_chat: bool = True
    hashtag_message_rarer_than: timedelta = times.FIVE_MINUTES


class BotConfig(BaseModel):
    token_secret_name: str  # must correspond to a valid secret in secret store
    feedback_handler_config: Optional[FeedbackHandlerConfig] = None
    user_flow_config: Optional[UserFlowConfig] = None

    foo: int = 1
