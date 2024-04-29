import json
from pathlib import Path
from typing import Optional

from aiohttp import web

from telebot_constructor.debug import DEBUG
from telebot_constructor.user_flow.blocks.constants import (
    FORM_CANCEL_CMD,
    FORM_SKIP_FIELD_CMD,
)

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


_PREFILLED_MESSAGES_JSON: Optional[str] = None


def get_prefilled_messages() -> str:
    global _PREFILLED_MESSAGES_JSON
    if _PREFILLED_MESSAGES_JSON is None:
        path = Path(__file__).parent / "data/prefilled_messages.json"
        with open(path, "r") as f:
            raw = json.load(f)
        # replacing placeholders with /commands, see form field for details
        for key in raw["cancel_command_is"]:
            raw["cancel_command_is"][key] = raw["cancel_command_is"][key].format(FORM_CANCEL_CMD)
        for key in raw["field_is_skippable"]:
            raw["field_is_skippable"][key] = raw["field_is_skippable"][key].format(FORM_SKIP_FIELD_CMD)
        supported_cmds = f"{FORM_SKIP_FIELD_CMD}, {FORM_CANCEL_CMD}"
        for key in raw["unsupported_command"]:
            raw["unsupported_command"][key] = raw["unsupported_command"][key].format(supported_cmds)
        _PREFILLED_MESSAGES_JSON = json.dumps(raw)
    return _PREFILLED_MESSAGES_JSON
