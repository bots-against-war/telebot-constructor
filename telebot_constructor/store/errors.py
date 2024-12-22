import asyncio
import logging
import time
import traceback
from dataclasses import dataclass
from typing import Any

import pydantic
from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.generic import KeyListStore

from telebot_constructor.constants import CONSTRUCTOR_PREFIX
from telebot_constructor.utils import page_params_to_redis_indices


class BotError(pydantic.BaseModel):
    timestamp: float
    message: str  # message used in logger.error("some message")
    exc_type: str | None = None  # "KeyError", "ValueError", etc
    exc_traceback: str | None = None  # multiline string with exception traceback

    @classmethod
    def from_log_record(cls, record: logging.LogRecord) -> "BotError":
        try:
            exc_type_str: str | None = record.exc_info[0].__name__  # type: ignore
        except Exception:
            exc_type_str = None

        try:
            exc_traceback: str | None = "\n".join(traceback.format_tb(record.exc_info[2]))  # type: ignore
        except Exception:
            exc_traceback = None

        return BotError(
            timestamp=time.time(),
            message=record.getMessage(),
            exc_type=exc_type_str,
            exc_traceback=exc_traceback,
        )


class StoringErrorsLogHandler(logging.Handler):
    def __init__(self, store: "BotErrorsStore", owner_id: str, bot_id: str) -> None:
        logging.Handler.__init__(self, level=logging.ERROR)
        self._store = store
        self._owner_id = owner_id
        self._bot_id = bot_id
        self._tasks: set[asyncio.Task[int]] = set()

    def emit(self, record: Any) -> None:
        if not isinstance(record, logging.LogRecord):
            return
        task = asyncio.create_task(
            self._store.save_error(
                owner_id=self._owner_id,
                bot_id=self._bot_id,
                e=BotError.from_log_record(record),
            )
        )
        task.add_done_callback(self._tasks.discard)
        self._tasks.add(task)


class BotErrorsStore:
    STORE_PREFIX = f"{CONSTRUCTOR_PREFIX}/errors"

    def __init__(self, redis: RedisInterface) -> None:
        self._bot_errors_store = KeyListStore[BotError](
            name="errors",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=None,
            loader=BotError.model_validate_json,
            dumper=BotError.model_dump_json,
        )

    def adapter_for(self, owner_id: str, bot_id: str) -> "BotSpecificErrorsStore":
        return BotSpecificErrorsStore(
            store=self,
            owner_id=owner_id,
            bot_id=bot_id,
        )

    def _error_store_key(self, owner_id: str, bot_id: str) -> str:
        return f"{owner_id}/{bot_id}"

    async def save_error(self, owner_id: str, bot_id: str, e: BotError) -> int:
        return await self._bot_errors_store.push(
            key=self._error_store_key(owner_id, bot_id),
            item=e,
            reset_ttl=False,
        )

    def instrument(self, logger: logging.Logger, owner_id: str, bot_id: str) -> None:
        logger.addHandler(
            StoringErrorsLogHandler(
                store=self,
                owner_id=owner_id,
                bot_id=bot_id,
            )
        )

    async def load_errors(self, username: str, bot_id: str, offset: int, count: int) -> list[BotError]:
        start, end = page_params_to_redis_indices(offset, count)
        return (
            await self._bot_errors_store.slice(
                key=self._error_store_key(username, bot_id),
                start=start,
                end=end,
            )
            or []
        )


@dataclass
class BotSpecificErrorsStore:
    store: BotErrorsStore
    owner_id: str
    bot_id: str

    def instrument(self, logger: logging.Logger) -> None:
        self.store.instrument(logger, owner_id=self.owner_id, bot_id=self.bot_id)
