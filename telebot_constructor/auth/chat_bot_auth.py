import datetime
import logging
import secrets
from pathlib import Path
from typing import Optional

from aiohttp import hdrs, web
from telebot import AsyncTeleBot
from telebot import types as tg
from telebot.runner import BotRunner
from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.generic import KeyValueStore

from telebot_constructor.app_models import AuthType, LoggedInUser
from telebot_constructor.auth.auth import Auth
from telebot_constructor.static import static_file_content


class ChatBotAuth(Auth):
    """
    Telegram bot based auth. You need to have a bot.

    - когда бот авторизации получает команду старт, он должен сгенерировать логин код и сохранить связи:
    1. "старт параметр - аккаунт юзерки" (и детали типа юзернейма аватарки и тд);
    2. "старт параметр - логин код";

    И прислать логин код юзерке в чат


    - юзерка должна ввести этот код в окошко на веб странице, класс авторизации верифицирует его через двойной лукап
    (логин код -> старт параметр -> данные аккаунта юзерки),

    генерирует access token, сохраняет финальную связь "аксесс токен - данные юзерки"
    и возвращает токен в Set-Cookie хедере (аналогично group chat auth)



    1. "старт параметр - chat.id"  start_param_store
    2. "логин код - старт параметр"       access_code_store
    3. "аксесс токен - аккаунт юзерки"     access_tokens_store
    """

    CONST_KEY = "const"
    STORE_PREFIX = "bot-auth"

    def __init__(
        self,
        redis: RedisInterface,
        bot: AsyncTeleBot,
        confirmation_code_lifetime: datetime.timedelta = datetime.timedelta(minutes=10),
        access_token_lifetime: datetime.timedelta = datetime.timedelta(days=1),
    ):
        self.bot = bot
        self.bot_username: Optional[str] = None
        self.logger = logging.getLogger(__name__ + f"[{self.__class__.__name__}]")
        self.access_code_store = KeyValueStore[str](
            name="access-code",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=confirmation_code_lifetime,
            dumper=lambda x: x,
            loader=lambda x: x,
        )
        self.access_tokens_store = KeyValueStore[int](
            name="access-tokens",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=access_token_lifetime,
        )
        self.start_param_store = KeyValueStore[int](
            name="start-param",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=access_token_lifetime,
        )

    async def get_auth_user(self) -> tg.User:
        pass

    async def get_bot_username(self) -> str:
        if self.bot_username is None:
            self.bot_username = (await self.bot.get_me()).username
        return self.bot_username

    ACCESS_TOKEN_COOKIE_NAME = "tc_access_token"

    async def authenticate_request(self, request: web.Request) -> Optional[LoggedInUser]:
        token = request.cookies.get(self.ACCESS_TOKEN_COOKIE_NAME)
        if token is None:
            self.logger.info("No auth cookie found in request")
            return None
        if not (await self.access_tokens_store.exists(token)):
            self.logger.info("Invalid auth cookie in request")
            return None
        self.logger.info("Auth OK")
        # TODO we need to implement get_auth_user
        # auth_user = await self.get_auth_user()

        user_chat_id = await self.access_tokens_store.load(token)

        return LoggedInUser(
            username="TG User",
            name=f"TG User №{user_chat_id}",
            auth_type=AuthType.TELEGRAM_BOT_AUTH,
            userpic=None,
        )

    async def unauthenticated_client_response(self, request: web.Request, static_files_dir: Path) -> web.Response:
        return web.Response(
            body=static_file_content(static_files_dir / "bot_auth_login.html"),
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
            if not await self.access_code_store.exists(code):
                self.logger.info("Invalid confirmation code submitted")
                raise web.HTTPUnauthorized()
            start_param = await self.access_code_store.load(code)
            chat_id = await self.start_param_store.load(start_param)
            access_token = secrets.token_hex(nbytes=32)
            self.logger.info("Confirmation code OK, issuing access token")
            if not await self.access_tokens_store.save(access_token, chat_id):
                raise web.HTTPInternalServerError()
            return web.Response(
                text="OK", headers={hdrs.SET_COOKIE: f"{self.ACCESS_TOKEN_COOKIE_NAME}={access_token}; Path=/"}
            )

        app.router.add_post("/bot-auth/login", login)

        async def request_bot_auth_link(request: web.Request) -> web.Response:
            """
            This method is called when user clicks on _____"Send code"_____ button on login page.
            That redirect user to telegram bot with unique start param.
            Example link: https://t.me/<bot_username>?start=<parameter>
            """
            start_param = secrets.token_hex(16)
            bot_username = await self.get_bot_username()
            link_to_bot = f"https://t.me/{bot_username}?start={start_param}"

            return web.Response(text=link_to_bot)

        app.router.add_post("/bot-auth/request-bot-auth-link", request_bot_auth_link)

    async def setup_bot(self) -> BotRunner:
        return await self.create_auth_bot(self.bot)

    async def create_auth_bot(self, bot: AsyncTeleBot) -> BotRunner:
        def extract_start_param(text):
            return text.split()[1] if len(text.split()) > 1 else None

        def in_storage(unique_code):
            # (pseudo-code) Should check if a unique code exists in storage
            return True

        def get_username_from_storage(unique_code):
            # (pseudo-code) Does a query to the storage, retrieving the associated username
            # Should be replaced by a real database-lookup.
            return "ABC" if in_storage(unique_code) else None

        def save_chat_id(chat_id, username):
            # (pseudo-code) Save the chat_id->username to storage
            # Should be replaced by a real database query.
            pass

        @bot.message_handler(commands=["start"])
        async def send_welcome(message):
            start_param = extract_start_param(message.text)
            if start_param:
                await self.start_param_store.save(start_param, message.chat.id)
                access_code = secrets.token_hex(16)
                await self.access_code_store.save(access_code, start_param)
                reply_text = f"🔑🔑🔑" f"\n\n" f"Введите этот код на сайте:" f"\n\n" f"<pre>{access_code}</pre>"

                await bot.reply_to(message, reply_text, parse_mode="HTML")

        return BotRunner(
            bot_prefix="auth_bot",
            bot=bot,
            background_jobs=[],
        )
