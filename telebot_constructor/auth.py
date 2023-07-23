import abc
from telebot_constructor.static import static_file_content
import datetime
from pathlib import Path
from typing import Optional

from aiohttp import web
from telebot import AsyncTeleBot
from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.generic import KeyValueStore

from telebot_constructor.debug import DEBUG


class Auth(abc.ABC):
    """Interface class for different ways to authorize web requests to bot constructor"""

    @abc.abstractmethod
    async def authenticate_request(self, request: web.Request) -> Optional[str]:
        """Request authentication, must return constructor's internal username (user id)"""
        ...

    @abc.abstractmethod
    async def unauthenticated_client_response(self, request: web.Request, static_files_dir: Path) -> web.Response:
        """Auth-specific response to the client; not used for API routes, only for browser clients"""
        ...


class NoAuth(Auth):
    """
    Dummy auth that lets anyone use the constructor and all of it's bots.
    Useful when running in a private network or during development.
    """

    async def authenticate_request(self, request: web.Request) -> Optional[str]:
        return "no-auth"

    async def unauthenticated_client_response(self, request: web.Request, static_files_dir: Path) -> web.Response:
        raise NotImplementedError()


class GroupChatAuth(Auth):
    """
    Telegram group chat based auth. You need to have a bot and a group chat it can send messages to.
    Everyone in the group chat will have shared access to the constructor.
    """

    CONST_KEY = "const"
    STORE_PREFIX = "group-chat-auth"

    def __init__(
        self,
        redis: RedisInterface,
        bot: AsyncTeleBot,
        auth_chat_id: int,
        confirmation_code_lifetime: datetime.timedelta = datetime.timedelta(minutes=10),
        access_token_lifetime: datetime.timedelta = datetime.timedelta(days=1),
    ):
        self.bot = bot
        self.auth_chat_id = auth_chat_id

        self.confirmation_code_store = KeyValueStore[str](
            name="confirmation-code",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=confirmation_code_lifetime,
            dumper=lambda x: x,
            loader=lambda x: x,
        )
        self.access_tokens_store = KeyValueStore[str](
            name="access-tokens",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=access_token_lifetime,
            dumper=lambda x: x,
            loader=lambda x: x,
        )

        self._cached_login_html: Optional[bytes] = None

    AUTH_COOKIE_NAME = "tc_access_token"

    async def authenticate_request(self, request: web.Request) -> Optional[str]:
        token = request.cookies.get(self.AUTH_COOKIE_NAME)
        if token is None:
            return None
        if not (await self.access_tokens_store.exists(token)):
            return None
        return "admin"  # all request are authenticated as the same user

    async def unauthenticated_client_response(self, request: web.Request, static_files_dir: Path) -> web.Response:
        return web.Response(
            body=static_file_content(static_files_dir / "group_chat_auth_login.html"),
            content_type="text/html",
        )
