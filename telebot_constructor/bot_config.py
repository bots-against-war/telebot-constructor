import pydantic


class BotConfig(pydantic.BaseModel):
    token: str  # dummy config for now
    admin_chat_id: int
