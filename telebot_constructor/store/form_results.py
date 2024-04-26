from dataclasses import dataclass
from typing import Any

from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.generic import KeyListStore

# there's no hope to model user-defined forms' results, so we use opaque type
OpaqueFormResult = dict[str, Any]


@dataclass
class GlobalFormId:
    username: str
    bot_id: str
    form_block_id: str


class FormResultsStore:
    def __init__(self, redis: RedisInterface) -> None:
        self._storage = KeyListStore[OpaqueFormResult](
            name="form-result-storage/",
            prefix="telebot-constructor",
            redis=redis,
            expiration_time=None,
        )

    def adapter_for(self, username: str, bot_id: str) -> "BotSpecificFormResultsStore":
        return BotSpecificFormResultsStore(
            storage=self,
            username=username,
            bot_id=bot_id,
        )

    def _composite_key(self, form_id: GlobalFormId) -> str:
        return "/".join([form_id.username, form_id.bot_id, form_id.form_block_id])

    async def save(self, form_id: GlobalFormId, result: OpaqueFormResult) -> bool:
        return (await self._storage.push(key=self._composite_key(form_id), item=result)) == 1

    async def load_page(self, form_id: GlobalFormId, offset: int, count: int) -> list[OpaqueFormResult]:
        start = -1 - offset  # offset 0 = last = -1, offset -1 = next-to-last = -2, etc
        end = start + count - 1  # redis indices are inclusive, so subtract one
        return (
            await self._storage.slice(
                key=self._composite_key(form_id),
                start=start,
                end=end,
            )
            or []
        )

    async def load_all(self, form_id: GlobalFormId) -> list[OpaqueFormResult]:
        key = self._composite_key(form_id)
        res: list[OpaqueFormResult] = []
        start = 0
        page_size = 100
        while True:
            page = await self._storage.slice(key, start, start + page_size - 1)
            if not page:
                break
            res.extend(page)
            start += len(page)
        return res


@dataclass
class BotSpecificFormResultsStore:
    """Small adapter to be passed to bot's internals"""

    storage: FormResultsStore
    username: str
    bot_id: str

    async def save(self, form_block_id: str, form_result: OpaqueFormResult) -> bool:
        return await self.storage.save(
            form_id=GlobalFormId(
                username=self.username,
                bot_id=self.bot_id,
                form_block_id=form_block_id,
            ),
            result=form_result,
        )
