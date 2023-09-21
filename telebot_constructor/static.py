from pathlib import Path

from aiohttp import web

from telebot_constructor.debug import DEBUG

STATIC_FILES_CACHE: dict[Path, bytes] = dict()


def static_file_content(path: Path) -> bytes:
    if not path.exists():
        raise web.HTTPNotFound(reason=f"Static path {path} does not exist")
    cached = STATIC_FILES_CACHE.get(path)
    if cached is not None:
        return cached
    data = path.read_bytes()
    if not DEBUG:
        STATIC_FILES_CACHE[path] = data
    return data
