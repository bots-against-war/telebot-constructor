import time

from telebot.metrics import TelegramUpdateMetrics, TelegramUpdateMetricsHandler
from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.generic import KeyListStore
from typing_extensions import TypedDict

from telebot_constructor.constants import CONSTRUCTOR_PREFIX
from telebot_constructor.utils import page_params_to_redis_indices


class BotError(TypedDict):
    timestamp: float
    update_metrics: TelegramUpdateMetrics


class MetricsStore:
    STORE_PREFIX = f"{CONSTRUCTOR_PREFIX}/metrics/"

    def __init__(self, redis: RedisInterface) -> None:
        self._errors_store = KeyListStore[BotError](
            name="errors",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=None,
        )

    def _error_store_key(self, username: str, bot_id: str) -> str:
        return f"{username}/{bot_id}"

    def get_update_metrics_handler(self, username: str, bot_id: str) -> TelegramUpdateMetricsHandler:

        async def handler(metrics: TelegramUpdateMetrics) -> None:
            exc_info = metrics.get("exception_info")
            if exc_info is not None:
                await self._errors_store.push(
                    self._error_store_key(username, bot_id),
                    BotError(
                        timestamp=time.time(),
                        update_metrics=metrics,
                    ),
                )

        return handler

    async def load_errors(self, username: str, bot_id: str, offset: int, count: int) -> list[BotError]:
        start, end = page_params_to_redis_indices(offset, count)
        return (
            await self._errors_store.slice(
                key=self._error_store_key(username, bot_id),
                start=start,
                end=end,
            )
            or []
        )
