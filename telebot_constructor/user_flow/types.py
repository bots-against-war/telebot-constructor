from dataclasses import dataclass
from typing import Awaitable, Callable, Optional

from telebot import AsyncTeleBot
from telebot import types as tg
from telebot.types import service as service_types
from telebot_components.redis_utils.interface import RedisInterface


@dataclass(frozen=True)
class UserFlowSetupContext:
    bot: AsyncTeleBot
    redis: RedisInterface


@dataclass(frozen=True)
class UserFlowContext:
    bot: AsyncTeleBot
    chat: Optional[tg.Chat]
    user: tg.User
    last_update_content: Optional[service_types.UpdateContent]


UserFlowBlockId = str

EnterUserFlowBlockCallback = Callable[[UserFlowBlockId, UserFlowContext], Awaitable[None]]
