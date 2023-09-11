import datetime
import logging

from pydantic import BaseModel
from telebot_components.feedback import (
    FeedbackConfig,
    FeedbackHandler,
    ServiceMessages,
    UserAnonymization,
)
from telebot_components.feedback.anti_spam import AntiSpam, AntiSpamConfig

from telebot_constructor.user_flow.blocks.base import UserFlowBlock
from telebot_constructor.user_flow.types import SetupResult, UserFlowContext, UserFlowSetupContext

logger = logging.getLogger(__name__)


class MessagesToUser(BaseModel):
    forwarded_to_admin_ok: str
    throttling: str


class MessagesToAdmin(BaseModel):
    copied_to_user_ok: str
    deleted_message_ok: str
    can_not_delete_message: str


class FeedbackHandlerConfig(BaseModel):
    admin_chat_id: int

    messages_to_user: MessagesToUser

    messages_to_admin: MessagesToAdmin

    anonimyze_users: bool

    max_messages_per_minute: float

    # hashtags config
    hashtags_in_admin_chat: bool
    unanswered_hashtag: str
    hashtag_message_rarer_than: datetime.timedelta

    # /log cmd config
    message_log_to_admin_chat: bool


class HumanOperatorBlock(UserFlowBlock):
    """Terminal block that incapsulates user interaction with a human operator"""

    feedback_handler_config: FeedbackHandlerConfig

    async def enter(self, context: UserFlowContext) -> None:
        pass  # nothing to do on enter

    async def setup(self, context: UserFlowSetupContext) -> SetupResult:
        log_prefix = f"[{context.bot_prefix}]"
        logger.info(log_prefix + "Setting up feedback handler")
        feedback_handler = FeedbackHandler(
            admin_chat_id=self.feedback_handler_config.admin_chat_id,
            redis=context.redis,
            bot_prefix=context.bot_prefix,
            config=FeedbackConfig(
                message_log_to_admin_chat=self.feedback_handler_config.message_log_to_admin_chat,
                force_category_selection=False,
                hashtags_in_admin_chat=self.feedback_handler_config.hashtags_in_admin_chat,
                hashtag_message_rarer_than=self.feedback_handler_config.hashtag_message_rarer_than,
                unanswered_hashtag=self.feedback_handler_config.unanswered_hashtag,
                confirm_forwarded_to_admin_rarer_than=None,
                user_anonymization=(
                    UserAnonymization.FULL if self.feedback_handler_config.anonimyze_users else UserAnonymization.NONE
                ),
            ),
            anti_spam=AntiSpam(
                context.redis,
                context.bot_prefix,
                config=AntiSpamConfig(
                    throttle_after_messages=int(5 * self.feedback_handler_config.max_messages_per_minute),
                    throttle_duration=datetime.timedelta(minutes=5),
                    soft_ban_after_throttle_violations=10,
                    soft_ban_duration=datetime.timedelta(days=1),
                ),
            ),
            service_messages=ServiceMessages(
                forwarded_to_admin_ok=self.feedback_handler_config.messages_to_user.forwarded_to_admin_ok,
                you_must_select_category=None,
                throttling_template=self.feedback_handler_config.messages_to_user.throttling,
                copied_to_user_ok=self.feedback_handler_config.messages_to_admin.copied_to_user_ok,
                can_not_delete_message=self.feedback_handler_config.messages_to_admin.can_not_delete_message,
                deleted_message_ok=self.feedback_handler_config.messages_to_admin.deleted_message_ok,
            ),
        )

        await feedback_handler.setup(context.bot)

        return SetupResult(
            background_jobs=feedback_handler.background_jobs(base_url=None, server_listening_future=None),
            aux_endpoints=await feedback_handler.aux_endpoints(),
        )
