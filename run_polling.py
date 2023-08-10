import asyncio
import logging
from pathlib import Path

from telebot_components.redis_utils.emulation import RedisEmulation
from telebot_components.utils.secrets import TomlFileSecretStore

from telebot_constructor.app import TelebotConstructorApp
from telebot_constructor.auth import NoAuth

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    redis = RedisEmulation()
    app = TelebotConstructorApp(
        redis=redis,
        auth=NoAuth(),
        secret_store=TomlFileSecretStore(Path("secrets.toml")),
        static_files_dir_override=Path("frontend/dist"),
    )
    await app.run_polling(port=8088)


if __name__ == "__main__":
    asyncio.run(main())
