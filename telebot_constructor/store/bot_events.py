from typing import Literal, TypedDict

from typing_extensions import NotRequired


class BotEventBase(TypedDict):
    timestamp: NotRequired[float]
    username: str


class BotStoppedEvent(BotEventBase):
    event: Literal["stopped"]


class BotDeletedEvent(BotEventBase):
    event: Literal["deleted"]


class BotStartedEvent(BotEventBase):
    event: Literal["started"]
    version: int


class BotEditedEvent(BotEventBase):
    event: Literal["edited"]
    new_version: int


BotEvent = BotStoppedEvent | BotDeletedEvent | BotStartedEvent | BotEditedEvent
