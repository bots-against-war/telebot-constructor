import collections
from typing import List

from telebot_constructor.user_flow.blocks.base import UserFlowBlock
from telebot_constructor.user_flow.entrypoints.base import UserFlowEntryPoint
from telebot_constructor.user_flow.types import (
    UserFlowBlockId,
    UserFlowContext,
    UserFlowSetupContext,
)


class UserFlow:
    def __init__(self, entrypoints: List[UserFlowEntryPoint], blocks: List[UserFlowBlock]):
        self.entrypoints = entrypoints
        self.block_by_id = {block.block_id: block for block in blocks}

        block_id_counter = collections.Counter(b.block_id for b in blocks)
        duplicate_block_ids = sorted(bid for bid, count in block_id_counter.items() if count > 1)
        if duplicate_block_ids:
            raise ValueError(f"Duplicate block ids detected: {duplicate_block_ids}")

    async def _enter_block(self, id: UserFlowBlockId, context: UserFlowContext) -> None:
        block = self.block_by_id.get(id)
        if block is None:
            raise ValueError(f"Attempt to enter non-existent block with id {id}")
        await block.enter(context, enter_block=self._enter_block)

    async def setup(self, context: UserFlowSetupContext) -> None:
        for entrypoint in self.entrypoints:
            await entrypoint.setup(context, enter_block=self._enter_block)
        for block in self.block_by_id.values():
            await block.setup(context, enter_block=self._enter_block)
