from dataclasses import dataclass
from typing import Awaitable, Callable, Coroutine, Optional

from telebot import AsyncTeleBot
from telebot import types as tg
from telebot.runner import AuxBotEndpoint
from telebot.types import service as service_types
from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.banned_users import BannedUsersStore


@dataclass(frozen=True)
class UserFlowSetupContext:
    bot_prefix: str
    bot: AsyncTeleBot
    redis: RedisInterface
    banned_users_store: BannedUsersStore
    enter_block: "EnterUserFlowBlockCallback"
    get_active_block_id: "GetActiveUserFlowBlockId"


@dataclass(frozen=True)
class UserFlowContext:
    bot: AsyncTeleBot
    chat: Optional[tg.Chat]
    user: tg.User
    last_update_content: Optional[service_types.UpdateContent]
    enter_block: "EnterUserFlowBlockCallback"
    get_active_block_id: "GetActiveUserFlowBlockId"


UserFlowBlockId = str

EnterUserFlowBlockCallback = Callable[[UserFlowBlockId, UserFlowContext], Awaitable[None]]
GetActiveUserFlowBlockId = Callable[[int], Awaitable[Optional[UserFlowBlockId]]]


@dataclass(frozen=True)
class SetupResult:
    background_jobs: list[Coroutine[None, None, None]]
    aux_endpoints: list[AuxBotEndpoint]

    @classmethod
    def empty(cls) -> "SetupResult":
        return SetupResult([], [])

    def merge(self, other: "SetupResult") -> "SetupResult":
        return SetupResult(
            background_jobs=self.background_jobs + other.background_jobs,
            aux_endpoints=self.aux_endpoints + other.aux_endpoints,
        )
