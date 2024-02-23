import datetime
import logging
import time
from typing import AsyncGenerator, TypedDict
from typing_extensions import NotRequired

from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.generic import (
    KeyDictStore,
    KeyListStore,
    KeyVersionedValueStore,
)

from telebot_constructor.app_models import BotTimestamps
from telebot_constructor.bot_config import BotConfig
from telebot_constructor.store.types import BotEvent, BotVersion

logger = logging.getLogger(__name__)


class BotConfigVersionMetadata(TypedDict):
    timestamp: NotRequired[float]
    message: str | None


def set_current_timestamp(data: BotConfigVersionMetadata | BotEvent):
    if "timestamp" not in data:
        data["timestamp"] = time.time()


class TelebotConstructorStore:
    """Main application storage for bot configs and their status"""

    STORE_PREFIX = "telebot-constructor"

    def __init__(self, redis: RedisInterface) -> None:
        # username + bot id composite key -> versioned bot config
        self._config_store = KeyVersionedValueStore[BotConfig, BotConfigVersionMetadata](
            name="config",
            prefix=self.STORE_PREFIX,
            redis=redis,
            snapshot_dumper=lambda config: config.model_dump(mode="json"),
            snapshot_loader=BotConfig.model_validate,
        )

        # username -> bot id -> currently running version
        # the version here is either:
        # - a number corresponding to a bot config version
        # - "stub" for a stub bot (e.g. for chat discovery)
        self._running_version_store = KeyDictStore[BotVersion](
            name="running-version",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=None,
        )

        # username + bot id composite key -> list of events that happened to bot
        self._bot_events_store = KeyListStore[BotEvent](
            name="bot-events",
            prefix=self.STORE_PREFIX,
            redis=redis,
        )

    # bot config store CRUD

    def _composite_key(self, username: str, bot_id: str) -> str:
        return f"{username}/{bot_id}"

    async def load_bot_config(self, username: str, bot_id: str, version: BotVersion = -1) -> BotConfig | None:
        load_version = version if version != "stub" else -1
        if res := await self._config_store.load_version(
            self._composite_key(username, bot_id),
            version=load_version,
        ):
            config, _version_meta = res
            if version == "stub":
                return config.stub()
            else:
                return config
        else:
            return None

    async def save_bot_config(
        self,
        username: str,
        bot_id: str,
        config: BotConfig,
        meta: BotConfigVersionMetadata,
    ) -> bool:
        set_current_timestamp(meta)
        return await self._config_store.save(self._composite_key(username, bot_id), config, meta)

    async def remove_bot_config(self, username: str, bot_id: str) -> bool:
        return await self._config_store.drop(self._composite_key(username, bot_id))

    async def bot_config_version_count(self, username: str, bot_id: str) -> int:
        return await self._config_store.count_versions(self._composite_key(username, bot_id))

    async def list_bot_ids(self, username: str) -> list[str]:
        keys = await self._config_store.find_keys(pattern=self._composite_key(username, "*"))
        prefix = self._composite_key(username, "")
        return [k.removeprefix(prefix) for k in keys]

    # running status methods

    async def is_bot_running(self, username: str, bot_id: str) -> bool:
        return await self._running_version_store.get_subkey(username, bot_id) is not None

    async def set_bot_not_running(self, username: str, bot_id: str) -> bool:
        return await self._running_version_store.remove_subkey(username, bot_id)

    async def set_bot_running_version(self, username: str, bot_id: str, version: BotVersion) -> bool:
        return await self._running_version_store.set_subkey(username, bot_id, version)

    async def get_bot_running_version(self, username: str, bot_id: str) -> BotVersion | None:
        return await self._running_version_store.get_subkey(username, bot_id)

    async def iter_running_bot_versions(self) -> AsyncGenerator[tuple[str, str, BotVersion], None]:
        usernames = await self._running_version_store.list_keys()
        for username in usernames:
            bot_versions = await self._running_version_store.load(username)
            for bot_id, version in bot_versions.items():
                yield username, bot_id, version

    # bot event log methods

    async def save_event(self, username: str, bot_id: str, event: BotEvent) -> bool:
        set_current_timestamp(event)
        return await self._bot_events_store.push(self._composite_key(username, bot_id), event) == 1

    async def load_timestamps(self, username: str, bot_id: str) -> BotTimestamps | None:
        events = await self._bot_events_store.all(self._composite_key(username, bot_id))
        if not events:
            return None
        try:
            edited_events = [e for e in events if e["event"] == "edited"]
            started_events = [e for e in events if e["event"] == "started"]
            deleted_events = [e for e in events if e["event"] == "deleted"]
            return BotTimestamps(
                created_at=datetime.datetime.fromtimestamp(events[0]["timestamp"], datetime.timezone.utc),
                last_updated_at=datetime.datetime.fromtimestamp(edited_events[-1]["timestamp"], datetime.timezone.utc),
                last_run_at=(
                    datetime.datetime.fromtimestamp(started_events[-1]["timestamp"], datetime.timezone.utc)
                    if started_events
                    else None
                ),
                deleted_at=(
                    datetime.datetime.fromtimestamp(deleted_events[-1]["timestamp"], datetime.timezone.utc)
                    if deleted_events
                    else None
                ),
            )
        except Exception:
            logger.exception("Error constructing bot timestamps object from event log, ignoring")
            return None
