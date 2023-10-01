import collections
import datetime
import logging
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

logger = logging.getLogger(__name__)


@dataclass
class UserFlow:
    entrypoints: List[UserFlowEntryPoint]
    blocks: List[UserFlowBlock]

    def __post_init__(self) -> None:
        self._active_block_id_store: Optional[KeyValueStore[str]] = None

        block_id_counter = collections.Counter(b.block_id for b in self.blocks)
        duplicate_block_ids = sorted(bid for bid, count in block_id_counter.items() if count > 1)
        if duplicate_block_ids:
            raise ValueError(f"Duplicate block ids: {duplicate_block_ids}")
        self.block_by_id = {block.block_id: block for block in self.blocks}

        catch_all_entities = [entrypoint for entrypoint in self.entrypoints if entrypoint.is_catch_all()] + [
            block for block in self.blocks if block.is_catch_all()
        ]
        if len(catch_all_entities) > 1:
            raise ValueError(
                f"More than one catch-all blocks/entrypoints: {', '.join(str(e) for e in catch_all_entities)}"
            )

    @property
    def active_block_id_store(self) -> KeyValueStore[str]:
        if self._active_block_id_store is None:
            raise RuntimeError("Active block id is not properly initialized, probably accessed before setup")
        return self._active_block_id_store

    async def _enter_block(self, id: UserFlowBlockId, context: UserFlowContext) -> None:
        if await context.banned_users_store.is_banned(context.user.id):
            return
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
        for idx, entrypoint in enumerate(self.entrypoints):
            logger.info(f"[{bot_prefix}] Setting up entrypoint {idx + 1} / {len(self.entrypoints)}: {entrypoint}")
            try:
                entrypoint_setup_result = await entrypoint.setup(setup_context)
            except Exception as e:
                raise ValueError(f"Error setting up {entrypoint}: {e}") from e
            result.merge(entrypoint_setup_result)
        for idx, block in enumerate(self.blocks):
            logger.info(f"[{bot_prefix}] Setting up block {idx + 1} / {len(self.blocks)}: {block}")
            try:
                block_setup_result = await block.setup(setup_context)
            except Exception as e:
                raise ValueError(f"Error setting up {block}: {e}") from e
            result.merge(block_setup_result)
        return result
