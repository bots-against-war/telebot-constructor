from dataclasses import dataclass

from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.generic import KeyListStore

# form results can have a lot of "internal" data types, but for this simple storage
# they're all cast to strings - CSV doesn't support anything complicated anyway!
FormResult = dict[str, str]


@dataclass
class GlobalFormId:
    username: str
    bot_id: str
    form_block_id: str


class FormResultsStore:
    def __init__(self, redis: RedisInterface) -> None:
        self._storage = KeyListStore[FormResult](
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

    async def save(self, form_id: GlobalFormId, result: FormResult) -> bool:
        return (await self._storage.push(key=self._composite_key(form_id), item=result)) == 1

    async def load_page(self, form_id: GlobalFormId, offset: int, count: int) -> list[FormResult]:
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

    async def load_all(self, form_id: GlobalFormId) -> list[FormResult]:
        key = self._composite_key(form_id)
        res: list[FormResult] = []
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

    async def save(self, form_block_id: str, form_result: FormResult) -> bool:
        return await self.storage.save(
            form_id=GlobalFormId(
                username=self.username,
                bot_id=self.bot_id,
                form_block_id=form_block_id,
            ),
            result=form_result,
        )
