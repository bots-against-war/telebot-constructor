from typing import NotRequired, TypedDict

from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.generic import KeyDictStore, KeyVersionedValueStore

from telebot_constructor.bot_config import BotConfig


class BotConfigVersionMetadata(TypedDict):
    timestamp: float
    message: NotRequired[str]


class TelebotConstructorStore:
    """Main application storage for bot configs and their status"""

    STORE_PREFIX = "telebot-constructor"

    def __init__(self, redis: RedisInterface) -> None:
        # username+name composite key -> versioned bot config
        self._config_store = KeyVersionedValueStore[BotConfig, BotConfigVersionMetadata](
            name="bot-configs-ver",
            prefix=self.STORE_PREFIX,
            redis=redis,
            snapshot_dumper=BotConfig.model_dump,
            snapshot_loader=BotConfig.model_validate,
        )
        # username -> name -> currently running version
        self._running_version_store = KeyDictStore[int](
            name="bot-running",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=None,
        )

    def _composite_key(self, username: str, bot_id: str) -> str:
        return f"{username}/{bot_id}"

    async def load_bot_config(self, username: str, bot_id: str, version: int | None = None) -> BotConfig | None:
        if res := await self._config_store.load_version(
            self._composite_key(username, bot_id),
            version=version or -1,
        ):
            config, _version_meta = res
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

    # async def list_running_versions(self) -> AsyncGenerator[tuple[str, str, int], None]:
    #     usernames = await self._running_version_store.list_keys()
    #     for username in usernames:

    async def set_bot_not_running(self, username: str, bot_id: str) -> bool:
        return await self._running_version_store.remove_subkey(username, bot_id)

    async def set_bot_running_version(self, username: str, bot_id: str, version: int) -> bool:
        return await self._running_version_store.set_subkey(username, bot_id, version)
