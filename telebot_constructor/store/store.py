import logging
import time
from typing import AsyncGenerator, Optional

from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.generic import (
    KeyDictStore,
    KeyListStore,
    KeyVersionedValueStore,
)

from telebot_constructor.app_models import BotInfo, BotVersionInfo
from telebot_constructor.bot_config import BotConfig
from telebot_constructor.constants import CONSTRUCTOR_PREFIX
from telebot_constructor.store.form_results import FormResultsStore
from telebot_constructor.store.metrics import MetricsStore
from telebot_constructor.store.types import (
    BotConfigVersionMetadata,
    BotEvent,
    BotVersion,
)

logger = logging.getLogger(__name__)


def set_current_timestamp(data: BotConfigVersionMetadata | BotEvent):
    if "timestamp" not in data:
        data["timestamp"] = time.time()


class TelebotConstructorStore:
    """Main application storage for bot configs and their status"""

    def __init__(self, redis: RedisInterface) -> None:
        # username + bot id composite key -> versioned bot config
        self._config_store = KeyVersionedValueStore[BotConfig, BotConfigVersionMetadata](
            name="config",
            prefix=CONSTRUCTOR_PREFIX,
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
            prefix=CONSTRUCTOR_PREFIX,
            redis=redis,
            expiration_time=None,
        )

        # username + bot id composite key -> list of events that happened to bot
        self._bot_events_store = KeyListStore[BotEvent](
            name="bot-events",
            prefix=CONSTRUCTOR_PREFIX,
            redis=redis,
        )

        # username -> bot id -> bot display name
        self._display_names_store = KeyDictStore[str](
            name="display-name",
            prefix=CONSTRUCTOR_PREFIX,
            redis=redis,
            expiration_time=None,
            dumper=str,
            loader=str,
        )

        self.form_results = FormResultsStore(redis=redis)

        self.metrics = MetricsStore(redis=redis)

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

    async def is_bot_exists(self, username: str, bot_id: str) -> bool:
        return await self.bot_config_version_count(username, bot_id) > 0

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

    async def save_bot_display_name(self, username: str, bot_id: str, display_name: str) -> bool:
        return await self._display_names_store.set_subkey(username, bot_id, display_name)

    async def load_bot_display_name(self, username: str, bot_id: str) -> Optional[str]:
        return await self._display_names_store.get_subkey(username, bot_id)

    async def load_bot_info(self, username: str, bot_id: str) -> Optional[BotInfo]:
        INCLUDE_LAST_EVENTS = 10
        INCLUDE_LAST_VERSIONS = 10
        INCLUDE_LAST_ERRORS = 10

        next_to_last_version = await self.bot_config_version_count(username, bot_id)
        if next_to_last_version == 0:
            return None

        display_name = await self.load_bot_display_name(username, bot_id) or bot_id

        last_events = await self._bot_events_store.tail(
            key=self._composite_key(username, bot_id), start=-INCLUDE_LAST_EVENTS
        )
        if not last_events:
            return None

        running_version = await self.get_bot_running_version(username, bot_id)
        if running_version == "stub":
            running_version = None

        # by default show 30 last versions
        first_shown_version = next_to_last_version - INCLUDE_LAST_VERSIONS
        # or, including running version and its close ancestors
        if running_version is not None:
            first_shown_version = min(first_shown_version, running_version - 3)
        first_shown_version = max(first_shown_version, 0)

        version_metadata = [
            v.meta
            for v in await self._config_store.load_raw_versions(
                self._composite_key(username, bot_id),
                start_version=first_shown_version,
            )
            if v.meta is not None  # this should always be true because we always set metadata
        ]
        if len(version_metadata) != next_to_last_version - first_shown_version:
            logger.error(
                f"[{username}][{bot_id}] Version metadata list has unexpected length: "
                + f"{len(version_metadata) = }, {next_to_last_version = }, {first_shown_version = }"
            )
            return None

        return BotInfo(
            bot_id=bot_id,
            display_name=display_name,
            running_version=running_version,
            last_versions=[
                BotVersionInfo(
                    version=version,
                    metadata=metadata,
                )
                for version, metadata in zip(range(first_shown_version, next_to_last_version), version_metadata)
            ],
            last_events=last_events,
            forms_with_responses=await self.form_results.list_forms(username, bot_id),
            last_errors=await self.metrics.load_errors(username, bot_id, offset=0, count=INCLUDE_LAST_ERRORS),
        )
