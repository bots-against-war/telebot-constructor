from typing import Literal

from typing_extensions import NotRequired, TypedDict


class BotConfigVersionMetadata(TypedDict):
    timestamp: NotRequired[float]
    message: str | None
    author_username: NotRequired[str | None]  # for shared bots


BotVersion = int | Literal["stub"]


class BotEventBase(TypedDict):
    timestamp: NotRequired[float]
    username: str  # internal constructor username, AKA actor id


class BotStoppedEvent(BotEventBase):
    event: Literal["stopped"]


class BotDeletedEvent(BotEventBase):
    event: Literal["deleted"]


class BotStartedEvent(BotEventBase):
    event: Literal["started"]
    version: BotVersion


class BotEditedEvent(BotEventBase):
    event: Literal["edited"]
    new_version: int


BotEvent = BotStoppedEvent | BotDeletedEvent | BotStartedEvent | BotEditedEvent
