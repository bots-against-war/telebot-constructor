import collections
import datetime
from dataclasses import dataclass
from typing import List, Optional

from telebot import AsyncTeleBot
from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.banned_users import BannedUsersStore
from telebot_components.stores.generic import KeyValueStore

from telebot_constructor.user_flow.blocks.base import UserFlowBlock
from telebot_constructor.user_flow.entrypoints.base import UserFlowEntryPoint
from telebot_constructor.user_flow.types import (
    SetupResult,
    UserFlowBlockId,
    UserFlowContext,
    UserFlowSetupContext,
)


@dataclass
class UserFlow:
    entrypoints: List[UserFlowEntryPoint]
    blocks: List[UserFlowBlock]

    def __post_init__(self) -> None:
        block_id_counter = collections.Counter(b.block_id for b in self.blocks)
        duplicate_block_ids = sorted(bid for bid, count in block_id_counter.items() if count > 1)
        if duplicate_block_ids:
            raise ValueError(f"Duplicate block ids: {duplicate_block_ids}")

        self.block_by_id = {block.block_id: block for block in self.blocks}

        self._active_block_id_store: Optional[KeyValueStore[str]] = None

    @property
    def active_block_id_store(self) -> KeyValueStore[str]:
        if self._active_block_id_store is None:
            raise RuntimeError("Active block id is not properly initialized, probably accessed before setup")
        return self._active_block_id_store

    async def _enter_block(self, id: UserFlowBlockId, context: UserFlowContext) -> None:
        block = self.block_by_id.get(id)
        if block is None:
            raise ValueError(f"Attempt to enter non-existent block with id {id}")
        await self.active_block_id_store.save(context.user.id, block.block_id)
        await block.enter(context)

    async def _get_active_block_id(self, user_id: int) -> Optional[UserFlowBlockId]:
        return await self.active_block_id_store.load(user_id)

    async def setup(
        self,
        bot_prefix: str,
        bot: AsyncTeleBot,
        redis: RedisInterface,
        banned_users_store: BannedUsersStore,
    ) -> SetupResult:
        setup_context = UserFlowSetupContext(
            bot_prefix=bot_prefix,
            bot=bot,
            redis=redis,
            banned_users_store=banned_users_store,
            enter_block=self._enter_block,
            get_active_block_id=self._get_active_block_id,
        )
        self._active_block_id_store = KeyValueStore[str](
            name="user-flow-active-block",
            prefix=bot_prefix,
            redis=redis,
            expiration_time=datetime.timedelta(days=14),
            dumper=str,
            loader=str,
        )
        result = SetupResult.empty()
        for entrypoint in self.entrypoints:
            new_result = await entrypoint.setup(setup_context)
            result.merge(new_result)
        for block in self.block_by_id.values():
            new_result = await block.setup(setup_context)
            result.merge(new_result)
        return result
