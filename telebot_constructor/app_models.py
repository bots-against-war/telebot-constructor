"""Pydantic models for various app endpoints"""


from pydantic import BaseModel


class BotTokenPayload(BaseModel):
    token: str
