import asyncio
import logging
import os
from pathlib import Path

from telebot import AsyncTeleBot
from telebot_components.redis_utils.emulation import RedisEmulation
from telebot_components.utils.secrets import TomlFileSecretStore

from telebot_constructor.app import TelebotConstructorApp
from telebot_constructor.auth import GroupChatAuth

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    redis = RedisEmulation()
    app = TelebotConstructorApp(
        redis=redis,
        auth=GroupChatAuth(
            redis=redis,
            bot=AsyncTeleBot(token=os.environ["GROUP_CHAT_AUTH_BOT_TOKEN"]),
            auth_chat_id=int(os.environ["GROUP_CHAT_AUTH_CHAT_ID"]),
        ),
        secret_store=TomlFileSecretStore(path=Path("secrets.toml")),
        static_files_dir_override=Path("frontend/public"),
    )
    await app.run_polling(port=8088)


if __name__ == "__main__":
    asyncio.run(main())
