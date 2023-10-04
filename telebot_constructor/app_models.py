"""Pydantic models for various app endpoints"""

import enum
from typing import Optional

from pydantic import BaseModel


class BotTokenPayload(BaseModel):
    token: str


class TgGroupChatType(enum.Enum):
    GROUP = "group"
    SUPERGROUP = "supergroup"
    CHANNEL = "channel"


class TgGroupChat(BaseModel):
    """pydantic projection of https://core.telegram.org/bots/api#chat"""

    id: int
    type: TgGroupChatType
    title: str
    description: Optional[str]
    username: Optional[str]
    is_forum: Optional[bool]
    photo: Optional[str]  # if set, base64-encoded chat photo
