import datetime
import operator
import time
from dataclasses import dataclass
from typing import Callable, Mapping, MutableMapping, cast

from pydantic import BaseModel
from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.generic import KeyDictStore, KeyListStore, KeyValueStore

from telebot_constructor.constants import CONSTRUCTOR_PREFIX
from telebot_constructor.utils import page_params_to_redis_indices

FieldId = str

# form results can have a lot of "internal" data types, but for this simple storage
# they're all cast to strings - CSV doesn't support anything complicated anyway!
FormResult = MutableMapping[FieldId, str | int | float]

# some keys reserved for internal usage
USER_KEY = "user"
TIMESTAMP_KEY = "timestamp"
RESERVED_FORM_FIELD_IDS = {TIMESTAMP_KEY, USER_KEY}


def empty_form_result() -> FormResult:
    return {TIMESTAMP_KEY: time.time()}


def noop(x: str) -> str:
    return x


@dataclass
class GlobalFormId:
    owner_id: str
    bot_id: str
    form_block_id: str

    def as_key(self) -> str:
        return "/".join([self.owner_id, self.bot_id, self.form_block_id])

    @classmethod
    def from_key(self, ck: str) -> "GlobalFormId":
        # this is simplistic, but user and bot ids are validated to not contain "/"
        # so, should be fine...
        parts = ck.split("/", maxsplit=2)
        if len(parts) != 3:
            raise ValueError(f"Error parsing composite key: {ck} -> {parts}")
        return GlobalFormId(owner_id=parts[0], bot_id=parts[1], form_block_id=parts[2])


class FormInfoBasic(BaseModel):
    form_block_id: str
    prompt: str
    title: str | None
    total_responses: int


class FormInfo(FormInfoBasic):
    field_names: dict[FieldId, str]


@dataclass
class FormResultsFilter:
    min_timestamp: float | None
    max_timestamp: float | None

    def describe(self) -> str:
        def fmt(ts: float):
            return datetime.datetime.fromtimestamp(ts).isoformat(timespec="minutes")

        start = fmt(self.min_timestamp) if self.min_timestamp is not None else "earliest"
        end = fmt(self.max_timestamp) if self.max_timestamp is not None else "latest"
        return f"{start} - {end}"

    @staticmethod
    def matches_timestamp(
        result: FormResult,
        filter_timestamp: float | None,
        cmp: Callable[[float, float], bool],
    ) -> bool:
        if filter_timestamp is None:
            return True
        result_timestamp = result.get(TIMESTAMP_KEY)
        if not isinstance(result_timestamp, float):
            return True
        return cmp(result_timestamp, filter_timestamp)

    def is_too_old(self, result: FormResult) -> bool:
        return not self.matches_timestamp(result, self.min_timestamp, cmp=operator.ge)

    def is_too_new(self, result: FormResult) -> bool:
        return not self.matches_timestamp(result, self.max_timestamp, cmp=operator.le)


class FormResultsStore:
    STORE_PREFIX = f"{CONSTRUCTOR_PREFIX}/form-results"

    def __init__(self, redis: RedisInterface) -> None:
        # list of responses/results for a particular form
        self._results_store = KeyListStore[FormResult](
            name="data",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=None,
        )
        # for each form, mapping field id -> field name to be displayed
        self._field_names_store = KeyDictStore[str](
            name="field-names",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=None,
            dumper=noop,
            loader=noop,
        )
        # form prompt, can be used as a title/identifier
        self._prompt_store = KeyValueStore[str](
            name="form-prompt",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=None,
            dumper=noop,
            loader=noop,
        )
        # dedicated form title that can be set by user, preferred over prompt
        self._title_store = KeyValueStore[str](
            name="form-title",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=None,
            dumper=noop,
            loader=noop,
        )

    def adapter_for(self, owner_id: str, bot_id: str) -> "BotSpecificFormResultsStore":
        return BotSpecificFormResultsStore(
            storage=self,
            owner_id=owner_id,
            bot_id=bot_id,
        )

    async def save(self, form_id: GlobalFormId, result: FormResult) -> bool:
        return (await self._results_store.push(key=form_id.as_key(), item=result)) == 1

    async def save_field_names(self, form_id: GlobalFormId, id_to_names: Mapping[str, str]) -> bool:
        return await self._field_names_store.set_multiple_subkeys(
            key=form_id.as_key(),
            subkey_to_value=id_to_names,  # type: ignore
        )

    async def save_form_title(self, form_id: GlobalFormId, title: str) -> bool:
        return await self._title_store.save(form_id.as_key(), title)

    async def save_form_prompt(self, form_id: GlobalFormId, prompt: str) -> bool:
        return await self._prompt_store.save(form_id.as_key(), prompt)

    async def list_forms(self, owner_id: str, bot_id: str) -> list[FormInfoBasic]:
        """Returns dict of bot id -> list of form block ids with saved data"""
        form_keys = await self._results_store.find_keys(
            pattern=GlobalFormId(
                owner_id,
                bot_id=bot_id,
                form_block_id="*",
            ).as_key()
        )

        global_form_ids = [GlobalFormId.from_key(key) for key in form_keys]
        if invalid_form_ids := [
            gfid for gfid in global_form_ids if (gfid.owner_id != owner_id or bot_id != gfid.bot_id)
        ]:
            raise ValueError(
                f"Parsed global form ids not matching the query: {owner_id = } {bot_id = } {invalid_form_ids = }"
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
                total_responses=await self._results_store.length(global_form_id.as_key()),
            )
            for global_form_id, prompt, title in zip(global_form_ids, prompts, titles)
        ]

    async def load_form_info(self, form_id: GlobalFormId) -> FormInfo | None:
        key = form_id.as_key()
        prompt = await self._prompt_store.load(key)
        if prompt is None:
            return None  # we consider only prompt as a mandatory field, no prompt = form not found
        return FormInfo(
            form_block_id=form_id.form_block_id,
            prompt=prompt,
            title=await self._title_store.load(key),
            field_names=await self._field_names_store.load(key),
            total_responses=await self._results_store.length(key),
        )

    async def load_page(self, form_id: GlobalFormId, offset: int, count: int) -> list[FormResult]:
        start, end = page_params_to_redis_indices(offset, count)
        return (
            await self._results_store.slice(
                key=form_id.as_key(),
                start=start,
                end=end,
            )
            or []
        )

    async def load(
        self,
        form_id: GlobalFormId,
        filter: FormResultsFilter,
        load_page_size: int = 100,
        max_results_count: int = 10_000,
    ) -> tuple[list[FormResult], bool]:
        key = form_id.as_key()
        results: list[FormResult] = []
        start = 0
        while len(results) < max_results_count:
            page = await self._results_store.slice(key, start, start + load_page_size - 1)
            if not page:
                # no more results to load
                return results, True
            start += len(page)
            for r in page:
                if filter.is_too_new(r):
                    # results are ordered chronologically, so we return as soon as
                    # we see the results that's too new
                    return results, True
                if filter.is_too_old(r):
                    continue
                results.append(r)
        return results, False


@dataclass
class BotSpecificFormResultsStore:
    """Small adapter to be passed to bot's internals"""

    storage: FormResultsStore
    owner_id: str
    bot_id: str

    async def save_form_result(
        self,
        form_block_id: str,
        form_result: FormResult,
        field_names: Mapping[FieldId, str],
        prompt: str,
    ) -> bool:
        form_id = GlobalFormId(owner_id=self.owner_id, bot_id=self.bot_id, form_block_id=form_block_id)
        return all(
            (
                await self.storage.save(form_id, result=form_result),
                await self.storage.save_field_names(form_id, id_to_names=field_names),
                await self.storage.save_form_prompt(form_id, prompt),
            )
        )
