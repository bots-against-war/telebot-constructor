import pydantic


class BotConfig(pydantic.BaseModel):
    token_secret_name: str  # must correspond to a valid secret in secret store
