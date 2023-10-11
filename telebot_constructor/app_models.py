"""Pydantic models for various app endpoints"""

import enum
from typing import Optional

from pydantic import BaseModel
from telebot import types as tg


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


class TgBotUser(BaseModel):
    """Info on telegram bot, combining info from several Bot API endpoints"""

    id: int

    # as returned by getMe
    first_name: str
    last_name: Optional[str]
    username: str

    # as returned by getMyXxx, potentially localizable (we're not using this for now though)
    description: Optional[str]
    short_description: Optional[str]

    can_join_groups: bool
    can_read_all_group_messages: bool

    commands: list[tg.BotCommand]

    userpic: Optional[str]  # base64-encoded bot's avatar photo preview
