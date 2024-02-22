from typing import AsyncGenerator, Literal, TypedDict

from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.generic import KeyDictStore, KeyVersionedValueStore

from telebot_constructor.bot_config import BotConfig


class BotConfigVersionMetadata(TypedDict):
    timestamp: float
    message: str | None


BotVersion = int | Literal["stub"]


class TelebotConstructorStore:
    """Main application storage for bot configs and their status"""

    STORE_PREFIX = "telebot-constructor"

    def __init__(self, redis: RedisInterface) -> None:
        # username+name composite key -> versioned bot config
        self._config_store = KeyVersionedValueStore[BotConfig, BotConfigVersionMetadata](
            name="config",
            prefix=self.STORE_PREFIX,
            redis=redis,
            snapshot_dumper=BotConfig.model_dump,
            snapshot_loader=BotConfig.model_validate,
        )
        # username -> name -> currently running version
        # the version here is either:
        # - a number corresponding to a bot config version
        # - "stub" for a stub bot (e.g. for chat discovery)
        self._running_version_store = KeyDictStore[BotVersion](
            name="running-version",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=None,
        )

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
        return await self._config_store.save(self._composite_key(username, bot_id), config, meta)

    async def remove_bot_config(self, username: str, bot_id: str) -> bool:
        return await self._config_store.drop(self._composite_key(username, bot_id))

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
