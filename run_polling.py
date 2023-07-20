import asyncio
import logging

from telebot_components.redis_utils.emulation import RedisEmulation

from telebot_constructor.app import TelebotConstructorApp

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    app = TelebotConstructorApp(redis=RedisEmulation())
    await app.run_polling(port=8088)


if __name__ == "__main__":
    asyncio.run(main())
