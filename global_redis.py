from urllib.parse import urlparse

from redis.asyncio import Redis  # type: ignore
from telebot_components.redis_utils.emulation import PersistentRedisEmulation
from telebot_components.redis_utils.interface import RedisInterface

import config

GLOBAL_REDIS: RedisInterface

if config.REDIS_URL is not None:
    if config.IS_HEROKU and config.IS_PROD:  # using SSL only in prod deployment
        redis_kwargs = {
            "ssl": True,
            "ssl_cert_reqs": None,
        }
    else:
        redis_kwargs = {}

    redis_url = urlparse(config.REDIS_URL)
    GLOBAL_REDIS = Redis(
        host=redis_url.hostname,
        port=redis_url.port,
        username=redis_url.username,
        password=redis_url.password,
        **redis_kwargs,
    )
else:
    GLOBAL_REDIS = PersistentRedisEmulation()  # type: ignore


async def cleanup_redis():
    global GLOBAL_REDIS
    if isinstance(GLOBAL_REDIS, Redis):
        await GLOBAL_REDIS.close()
    del GLOBAL_REDIS
