import asyncio
import logging
import os
from pathlib import Path
from urllib.parse import urlparse

from redis.asyncio import Redis  # type: ignore

# from telebot_components.redis_utils.emulation import PersistentRedisEmulation
# from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.utils.secrets import RedisSecretStore

from telebot_constructor.app import TelebotConstructorApp
from telebot_constructor.auth import NoAuth

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    redis_url = urlparse(os.environ.get("REDIS_URL"))
    redis = Redis(
        host=redis_url.hostname,
        port=redis_url.port,
        username=redis_url.username,
        password=redis_url.password,
    )
    # redis = PersistentRedisEmulation()  # type: ignore

    secret_store = RedisSecretStore(
        redis=redis,
        encryption_key=str(os.environ.get("SECRETS_ENCRYPTION_KEY")),
        secret_max_len=10 * 1024,
        secrets_per_user=10,
        scope_secrets_to_user=False,
    )
    # secret_store = TomlFileSecretStore(path=Path(__file__).parent.parent / "secrets.toml")

    app = TelebotConstructorApp(
        redis=redis,
        auth=NoAuth(),
        secret_store=secret_store,
        static_files_dir_override=Path("frontend/dist"),
    )
    await app.run_polling(port=int(os.environ.get("PORT", 8088)))


if __name__ == "__main__":
    asyncio.run(main())
