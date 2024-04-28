from dataclasses import dataclass

from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.generic import KeyDictStore, KeyListStore, KeyValueStore

FieldId = str

# form results can have a lot of "internal" data types, but for this simple storage
# they're all cast to strings - CSV doesn't support anything complicated anyway!
FormResult = dict[FieldId, str]


def noop(x: str) -> str:
    return x


@dataclass
class GlobalFormId:
    username: str
    bot_id: str
    form_block_id: str


class FormResultsStore:
    PREFIX = "telebot-constructor/form-results"

    def __init__(self, redis: RedisInterface) -> None:
        # list of responses/results for a particular form
        self._results_store = KeyListStore[FormResult](
            name="data",
            prefix=self.PREFIX,
            redis=redis,
            expiration_time=None,
        )
        # for each form, mapping field id -> field name to be displayed
        self._field_names_store = KeyDictStore[str](
            name="field-names",
            prefix=self.PREFIX,
            redis=redis,
            expiration_time=None,
            dumper=noop,
            loader=noop,
        )
        # form prompt, can be used as a title/identifier
        self._form_prompt_store = KeyValueStore[str](
            name="form-prompt",
            prefix=self.PREFIX,
            redis=redis,
            expiration_time=None,
            dumper=noop,
            loader=noop,
        )
        # dedicated form title that can be set by user, preferred over prompt
        self._form_title_store = KeyValueStore[str](
            name="form-title",
            prefix=self.PREFIX,
            redis=redis,
            expiration_time=None,
            dumper=noop,
            loader=noop,
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
        return (await self._results_store.push(key=self._composite_key(form_id), item=result)) == 1

    async def save_field_names(self, form_id: GlobalFormId, id_to_names: dict[str, str]) -> bool:
        return await self._field_names_store.set_multiple_subkeys(
            key=self._composite_key(form_id),
            subkey_to_value=id_to_names,  # type: ignore
        )

    async def save_form_title(self, form_id: GlobalFormId, title: str) -> bool:
        return await self._form_title_store.save(self._composite_key(form_id), title)

    async def save_form_prompt(self, form_id: GlobalFormId, prompt: str) -> bool:
        return await self._form_prompt_store.save(self._composite_key(form_id), prompt)

    async def load_page(self, form_id: GlobalFormId, offset: int, count: int) -> list[FormResult]:
        # "offset" goes from last to earlier results
        end = -1 - offset  # offset 0 = last = -1, offset 1 = next-to-last = -2, etc
        start = end - (count - 1)  # redis indices are inclusive, so subtract one from count
        return (
            await self._results_store.slice(
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
            page = await self._results_store.slice(key, start, start + page_size - 1)
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

    async def save_form_result(
        self,
        form_block_id: str,
        form_result: FormResult,
        field_names: dict[FieldId, str],
        prompt: str,
    ) -> bool:
        form_id = GlobalFormId(username=self.username, bot_id=self.bot_id, form_block_id=form_block_id)
        return all(
            (
                await self.storage.save(form_id, result=form_result),
                await self.storage.save_field_names(form_id, id_to_names=field_names),
                await self.storage.save_form_prompt(form_id, prompt),
            )
        )
