from datetime import timedelta
from typing import Optional

from pydantic import BaseModel
from telebot_components.constants import times


class FeedbackHandlerConfig(BaseModel):
    admin_chat_id: int
    message_log_to_admin_chat: bool = True
    force_category_selection: bool = False
    hashtags_in_admin_chat: bool = True
    hashtag_message_rarer_than: timedelta = times.FIVE_MINUTES


class BotConfig(BaseModel):
    token_secret_name: str  # must correspond to a valid secret in secret store
    feedback_handler_config: Optional[FeedbackHandlerConfig] = None
