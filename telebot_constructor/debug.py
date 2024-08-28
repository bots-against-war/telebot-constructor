import asyncio
import os

from aiohttp import web
from aiohttp.typedefs import Handler

DEBUG = bool(os.getenv("TELEBOT_CONSTRUCTOR_DEBUG"))

if DEBUG:
    print("DEBUG MODE ON")

# useful for testing loading screens on frontend
SLEEP_BEFORE_REQUEST = float(os.environ.get("TELEBOT_CONSTRUCTOR_SLEEP_BEFORE_REQUEST", "0"))


def setup_debugging(app: web.Application) -> None:  # pragma: no cover
    if not DEBUG:
        return

    @web.middleware
    async def sleepy_middleware(request: web.Request, handler: Handler) -> web.StreamResponse:
        await asyncio.sleep(SLEEP_BEFORE_REQUEST)
        return await handler(request)

    app.middlewares.append(sleepy_middleware)
