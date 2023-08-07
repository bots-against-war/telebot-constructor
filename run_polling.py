import asyncio
import logging
import os
from pathlib import Path

from cryptography.fernet import Fernet
from telebot import AsyncTeleBot
from telebot_components.redis_utils.emulation import RedisEmulation
from telebot_components.utils.secrets import RedisSecretStore

from telebot_constructor.app import TelebotConstructorApp
from telebot_constructor.auth import GroupChatAuth, NoAuth

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    redis = RedisEmulation()
    app = TelebotConstructorApp(
        redis=redis,
        auth=NoAuth(),
        secret_store=RedisSecretStore(redis, Fernet.generate_key().decode("utf-8"), 10, 100, True),
        static_files_dir_override=Path("frontend/dist"),
    )
    await app.run_polling(port=8088)


if __name__ == "__main__":
    asyncio.run(main())
