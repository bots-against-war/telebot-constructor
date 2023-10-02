import asyncio
import logging
import os
from pathlib import Path
from urllib.parse import urlparse

from redis.asyncio import Redis  # type: ignore
from telebot_components.redis_utils.emulation import PersistentRedisEmulation
from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.utils.secrets import (
    RedisSecretStore,
    SecretStore,
    TomlFileSecretStore,
)

from telebot_constructor.app import TelebotConstructorApp
from telebot_constructor.auth import NoAuth

logging.basicConfig(level=logging.DEBUG)


async def main() -> None:
    if bool(os.environ.get("TELEBOT_CONSTRUCTOR_SECRETS_USE_REDIS_EMULATION")):
        redis: RedisInterface = PersistentRedisEmulation()  # type: ignore
    else:
        redis_url = urlparse(os.environ["REDIS_URL"])
        redis = Redis(
            host=redis_url.hostname,
            port=redis_url.port,
            username=redis_url.username,
            password=redis_url.password,
        )

    if bool(os.environ.get("TELEBOT_CONSTRUCTOR_SECRETS_FROM_FILE")):
        secret_store: SecretStore = TomlFileSecretStore(path=Path(__file__).parent / "secrets.toml")
    else:
        secret_store = RedisSecretStore(
            redis=redis,
            encryption_key=os.environ["SECRETS_ENCRYPTION_KEY"],
            secret_max_len=10 * 1024,
            secrets_per_user=10,
            scope_secrets_to_user=False,
        )

    app = TelebotConstructorApp(
        redis=redis,
        auth=NoAuth(),
        secret_store=secret_store,
        static_files_dir_override=Path("frontend/dist"),
    )
    await app.run_polling(port=int(os.environ.get("PORT", 8088)))


if __name__ == "__main__":
    asyncio.run(main())
