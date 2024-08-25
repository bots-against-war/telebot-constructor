import abc
import asyncio
import base64
import datetime
import logging
import time
from typing import Optional

from telebot import AsyncTeleBot
from telebot_components.redis_utils.emulation import RedisEmulation
from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.generic import KeyValueStore

from telebot_constructor.constants import CONSTRUCTOR_PREFIX
from telebot_constructor.utils.rate_limit_retry import rate_limit_retry

logger = logging.getLogger(__name__)


class TelegramFilesDownloader(abc.ABC):
    """Thin wrapper around AsyncTeleBot methods to lookup and download file; handles caching and base64-encoding"""

    @abc.abstractmethod
    async def get_base64_file(self, bot: AsyncTeleBot, file_id: str) -> Optional[str]: ...

    @abc.abstractmethod
    async def setup(self) -> None: ...

    @abc.abstractmethod
    async def cleanup(self) -> None: ...


class RedisCacheTelegramFilesDownloader(TelegramFilesDownloader):
    STORE_PREFIX = f"{CONSTRUCTOR_PREFIX}/files-cache"

    def __init__(self, redis: RedisInterface, max_cached: int = 1024) -> None:
        self.redis = redis
        self.max_cached = max_cached
        self.cached_files_storage = KeyValueStore[str](
            name="tg-file",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=datetime.timedelta(days=60),
            dumper=str,
            loader=str,
        )
        self.last_accessed_storage = KeyValueStore[float](
            name="tg-file-last-accessed",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=datetime.timedelta(days=60),
        )
        self._task: asyncio.Task[None] | None = None

    async def get_base64_file(self, bot: AsyncTeleBot, file_id: str) -> str | None:
        cached_b64 = await self.cached_files_storage.load(file_id)
        await self.last_accessed_storage.save(file_id, time.time())
        if cached_b64 is not None:
            await self.cached_files_storage.touch(file_id)
            return cached_b64
        else:
            try:
                async for attempt in rate_limit_retry():
                    with attempt:
                        file = await bot.get_file(file_id)
                        file_bytes = await bot.download_file(file_path=file.file_path)
                file_b64 = base64.b64encode(file_bytes).decode("utf-8")
                await self.cached_files_storage.save(file_id, file_b64)
                return file_b64
            except Exception:
                logger.info("Error downloading file, ignoring", exc_info=True)
                return None

    async def _evict_extra_cached_files(self) -> None:
        cached_file_ids = await self.cached_files_storage.list_keys()
        total_cached_count = len(cached_file_ids)
        if total_cached_count < self.max_cached:
            return
        logger.info(
            f"Cached files count ({total_cached_count}) exceeds the limit ({self.max_cached}), starting cleanup"
        )
        last_accessed_times: dict[str, float] = dict()
        evict_file_ids: set[str] = set()
        for cached_file_id in cached_file_ids:
            last_used = await self.last_accessed_storage.load(cached_file_id)
            if last_used is None:
                evict_file_ids.add(cached_file_id)
            else:
                last_accessed_times[cached_file_id] = last_used
        if evict_file_ids:
            logger.info(f"Last access time not found for {len(evict_file_ids)} files, will evict them")

        access_order = sorted(last_accessed_times.items(), key=lambda key_time: key_time[1])
        evict_count = total_cached_count - self.max_cached
        evict_file_ids.union(file_id for file_id, _ in access_order[:evict_count])
        logger.info(f"Will evict a total of {len(evict_file_ids)} files")

        evicted_count = 0
        for file_id in evict_file_ids:
            try:
                await self.last_accessed_storage.drop(file_id)
                await self.cached_files_storage.drop(file_id)
                evicted_count += 1
            except Exception:
                logger.info(f"Error evicting file {file_id!r}, ignoring", exc_info=True)

        logger.info(f"Eviction completed ({evicted_count} / {len(evict_file_ids)} successful)")

    async def _evict_extra_cached_in_background(self) -> None:
        while True:
            await asyncio.sleep(10 * 60)  # 10 minutes
            try:
                await self._evict_extra_cached_files()
            except Exception:
                logger.exception("Unexpected error evicting extra cached files, will try next time")

    async def setup(self) -> None:
        if self._task is not None:
            return
        self._task = asyncio.create_task(
            self._evict_extra_cached_in_background(),
            name="Evicting extra files from telegram-downloaded files cache",
        )

    async def cleanup(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass


class InmemoryCacheTelegramFilesDownloader(RedisCacheTelegramFilesDownloader):
    def __init__(self) -> None:
        super().__init__(redis=RedisEmulation(), max_cached=1024)
