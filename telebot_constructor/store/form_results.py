from dataclasses import dataclass
from typing import cast

from pydantic import BaseModel
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

    def as_key(self) -> str:
        return "/".join([self.username, self.bot_id, self.form_block_id])

    @classmethod
    def from_key(self, ck: str) -> "GlobalFormId":
        # this is simplistic, but user and bot ids are validated to not contain "/"
        # so, should be fine...
        parts = ck.split("/", maxsplit=2)
        if len(parts) != 3:
            raise ValueError(f"Error parsing composite key: {ck} -> {parts}")
        return GlobalFormId(username=parts[0], bot_id=parts[1], form_block_id=parts[2])


class FormInfoBasic(BaseModel):
    form_block_id: str
    prompt: str
    title: str | None


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
        self._prompt_store = KeyValueStore[str](
            name="form-prompt",
            prefix=self.PREFIX,
            redis=redis,
            expiration_time=None,
            dumper=noop,
            loader=noop,
        )
        # dedicated form title that can be set by user, preferred over prompt
        self._title_store = KeyValueStore[str](
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

    async def save(self, form_id: GlobalFormId, result: FormResult) -> bool:
        return (await self._results_store.push(key=form_id.as_key(), item=result)) == 1

    async def save_field_names(self, form_id: GlobalFormId, id_to_names: dict[str, str]) -> bool:
        return await self._field_names_store.set_multiple_subkeys(
            key=form_id.as_key(),
            subkey_to_value=id_to_names,  # type: ignore
        )

    async def save_form_title(self, form_id: GlobalFormId, title: str) -> bool:
        return await self._title_store.save(form_id.as_key(), title)

    async def save_form_prompt(self, form_id: GlobalFormId, prompt: str) -> bool:
        return await self._prompt_store.save(form_id.as_key(), prompt)

    async def list_forms(self, username: str, bot_id: str) -> list[FormInfoBasic]:
        """Returns dict of bot id -> list of form block ids with saved data"""
        form_keys = await self._results_store.find_keys(
            pattern=GlobalFormId(
                username,
                bot_id=bot_id,
                form_block_id="*",
            ).as_key()
        )

        global_form_ids = [GlobalFormId.from_key(key) for key in form_keys]
        if invalid_form_ids := [
            gfid for gfid in global_form_ids if (gfid.username != username or bot_id != gfid.bot_id)
        ]:
            raise ValueError(
                f"Parsed global form ids not matching the query: {username = } {bot_id = } {invalid_form_ids = }"
            )

        prompts = await self._prompt_store.load_multiple(form_keys)
        if keys_without_prompt := [key for prompt, key in zip(prompts, form_keys) if prompt is None]:
            raise ValueError(f"Prompt not found for keys: {keys_without_prompt}")

        titles = await self._title_store.load_multiple(form_keys)

        return [
            FormInfoBasic(
                form_block_id=global_form_id.form_block_id,
                prompt=cast(str, prompt),  # see check above
                title=title,
            )
            for global_form_id, prompt, title in zip(global_form_ids, prompts, titles)
        ]

    async def load_page(self, form_id: GlobalFormId, offset: int, count: int) -> list[FormResult]:
        # "offset" goes from last to earlier results
        end = -1 - offset  # offset 0 = last = -1, offset 1 = next-to-last = -2, etc
        start = end - (count - 1)  # redis indices are inclusive, so subtract one from count
        return (
            await self._results_store.slice(
                key=form_id.as_key(),
                start=start,
                end=end,
            )
            or []
        )

    async def load_all(self, form_id: GlobalFormId) -> list[FormResult]:
        key = form_id.as_key()
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
