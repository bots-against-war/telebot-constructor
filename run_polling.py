import asyncio
import logging
import os
from pathlib import Path

from telebot_components.redis_utils.emulation import PersistentRedisEmulation
from telebot_components.utils.secrets import TomlFileSecretStore

from global_redis import GLOBAL_REDIS, cleanup_redis
from secret_store import secret_store
from telebot_constructor.app import TelebotConstructorApp
from telebot_constructor.auth import NoAuth

logging.basicConfig(level=logging.DEBUG)


async def main() -> None:
    redis = GLOBAL_REDIS
    app = TelebotConstructorApp(
        redis=redis,
        auth=NoAuth(),
        secret_store=secret_store,
        static_files_dir_override=Path("frontend/dist"),
    )
    await app.run_polling(port=int(os.environ.get("PORT", 8088)))


if __name__ == "__main__":
    asyncio.run(main())
