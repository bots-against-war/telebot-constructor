import abc
import datetime
import secrets
from pathlib import Path
from typing import Optional

from aiohttp import hdrs, web
from telebot import AsyncTeleBot
from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.generic import KeyValueStore

from telebot_constructor.static import static_file_content


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

    async def setup_routes(self, app: web.Application) -> None:
        """Optional setup hook for subclasses to override to add their login API routes"""
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

        self.access_code_store = KeyValueStore[str](
            name="access-code",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=confirmation_code_lifetime,
            dumper=lambda x: x,
            loader=lambda x: x,
        )
        self.access_tokens_store = KeyValueStore[None](
            name="access-tokens",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=access_token_lifetime,
            dumper=lambda x: "null",
            loader=lambda x: None,
        )

    ACCESS_TOKEN_COOKIE_NAME = "tc_access_token"

    async def authenticate_request(self, request: web.Request) -> Optional[str]:
        token = request.cookies.get(self.ACCESS_TOKEN_COOKIE_NAME)
        if token is None:
            return None
        if not (await self.access_tokens_store.exists(token)):
            return None
        return "admin"  # all request are authenticated as the same user

    async def unauthenticated_client_response(self, request: web.Request, static_files_dir: Path) -> web.Response:
        if not (await self.access_code_store.exists(self.CONST_KEY)):
            access_code = secrets.token_hex(16)
            await self.access_code_store.save(self.CONST_KEY, access_code)
            await self.bot.send_message(
                chat_id=self.auth_chat_id,
                text=f"🔑🔑🔑\nTelebot Constructor access code\n\n<pre>{access_code}</pre>",
                parse_mode="HTML",
            )
        return web.Response(
            body=static_file_content(static_files_dir / "group_chat_auth_login.html"),
            content_type="text/html",
        )

    async def setup_routes(self, app: web.Application) -> None:
        async def login(request: web.Request) -> web.Response:
            try:
                request_json = await request.json()
                code = request_json["code"]
            except KeyError:
                raise web.HTTPBadRequest(reason="Required `code` field not present in request body")
            except Exception:
                raise web.HTTPBadRequest(reason="Request body must be a valid JSON object")
            correct_code = await self.access_code_store.load(self.CONST_KEY)
            if correct_code != code:
                raise web.HTTPUnauthorized()
            access_token = secrets.token_hex(nbytes=32)
            if not await self.access_tokens_store.save(access_token, None):
                raise web.HTTPInternalServerError()
            return web.Response(text="OK", headers={hdrs.SET_COOKIE: f"{self.ACCESS_TOKEN_COOKIE_NAME}={access_token}"})

        app.router.add_post("/constructor/group-chat-auth-login", login)
