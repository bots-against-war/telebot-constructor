from pathlib import Path

from telebot_constructor.debug import DEBUG

STATIC_FILES_CACHE: dict[Path, bytes] = dict()


def static_file_content(path: Path) -> bytes:
    cached = STATIC_FILES_CACHE.get(path)
    if cached is not None:
        return cached
    data = path.read_bytes()
    if not DEBUG:
        STATIC_FILES_CACHE[path] = data
    return data
