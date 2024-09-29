import asyncio
import csv
import datetime
import fnmatch
import json
import logging
import mimetypes
import re
from io import StringIO
from pathlib import Path
from typing import Optional, Type, TypeVar

import pydantic
from aiohttp import hdrs, web
from aiohttp_swagger import setup_swagger  # type: ignore
from telebot import AsyncTeleBot
from telebot.runner import BotRunner
from telebot.util import create_error_logging_task
from telebot.webhook import WebhookApp
from telebot_components.language import LanguageData
from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.utils.secrets import SecretStore

from telebot_constructor.app_models import (
    BotErrorsPage,
    BotInfoList,
    BotTokenPayload,
    BotVersionsPage,
    FormResultsPage,
    LoggedInUser,
    SaveBotConfigVersionPayload,
    StartBotPayload,
    TgBotUser,
    TgBotUserUpdate,
    UpdateBotDisplayNamePayload,
)
from telebot_constructor.auth.auth import Auth
from telebot_constructor.bot_config import BotConfig
from telebot_constructor.build_time_config import BASE_PATH, VERSION
from telebot_constructor.construct import BotFactory, construct_bot, make_bare_bot
from telebot_constructor.cors import setup_cors
from telebot_constructor.debug import setup_debugging
from telebot_constructor.group_chat_discovery import GroupChatDiscoveryHandler
from telebot_constructor.runners import (
    ConstructedBotRunner,
    PollingConstructedBotRunner,
    WebhookAppConstructedBotRunner,
)
from telebot_constructor.static import get_prefilled_messages, static_file_content
from telebot_constructor.store.form_results import (
    TIMESTAMP_KEY,
    USER_KEY,
    FormResultsFilter,
    GlobalFormId,
)
from telebot_constructor.store.store import (
    BotConfigVersionMetadata,
    BotVersion,
    TelebotConstructorStore,
)
from telebot_constructor.store.types import (
    BotDeletedEvent,
    BotEditedEvent,
    BotStartedEvent,
    BotStoppedEvent,
)
from telebot_constructor.telegram_files_downloader import (
    InmemoryCacheTelegramFilesDownloader,
    TelegramFilesDownloader,
)
from telebot_constructor.utils import page_params_to_redis_indices

logger = logging.getLogger(__name__)


PydanticModelT = TypeVar("PydanticModelT", bound=pydantic.BaseModel)


class TelebotConstructorApp:
    """
    Main application class, managing aiohttp app setup (routes, middlewares) and running bots (via bot runner)
    """

    def __init__(
        self,
        redis: RedisInterface,
        auth: Auth,
        secret_store: SecretStore,
        static_files_dir: Path = Path(__file__).parent / "static",
        telegram_files_downloader: Optional[TelegramFilesDownloader] = None,
    ) -> None:
        self.auth = auth
        self.secret_store = secret_store
        self.static_files_dir = static_files_dir
        logger.info(f"Will serve static frontend files from {self.static_files_dir.absolute()}")
        self.redis = redis

        self.telegram_files_downloader = telegram_files_downloader or InmemoryCacheTelegramFilesDownloader()
        self.store = TelebotConstructorStore(redis)
        self.group_chat_discovery_handler = GroupChatDiscoveryHandler(
            redis=redis, telegram_files_downloader=self.telegram_files_downloader
        )

        # set during on of the setup/run methods to a concrete subclass
        self._runner: Optional[ConstructedBotRunner] = None
        self._bot_factory: BotFactory = AsyncTeleBot  # for overriding during tests

    @property
    def runner(self) -> ConstructedBotRunner:
        if self._runner is None:
            raise RuntimeError("Constructed bot runner was not initialized properly")
        return self._runner

    # region: request helpers
    # parse data from requests etc

    async def _authenticate_full(self, request: web.Request) -> LoggedInUser:
        try:
            logged_in_user = await self.auth.authenticate_request(request)
        except Exception:
            logger.exception("Error autorizing user")
            logged_in_user = None
        if logged_in_user is None:
            raise web.HTTPUnauthorized(reason="Authentication required")
        return logged_in_user

    async def authenticate(self, request: web.Request) -> str:
        logged_in_user = await self._authenticate_full(request)
        return logged_in_user.username

    # used for bot user and bot names
    VALID_NAME_RE = re.compile(r"^[0-9a-zA-Z\-_]{3,64}$")

    def _validate_name(self, name: str) -> None:
        if not self.VALID_NAME_RE.match(name):
            raise web.HTTPBadRequest(
                reason="Name must be 3-64 characters long and include only alphanumerics, hyphens and dashes"
            )

    def parse_path_part(self, request: web.Request, part_name: str) -> str:
        part = request.match_info.get(part_name)
        if part is None:
            raise web.HTTPNotFound()
        return part

    def parse_bot_id(self, request: web.Request, path_part_name: str = "bot_id") -> str:
        name = self.parse_path_part(request, path_part_name)
        self._validate_name(name)
        return name

    async def parse_body_as_model(self, request: web.Request, Model: Type[PydanticModelT]) -> PydanticModelT:
        try:
            return Model.model_validate(await request.json())
        except json.JSONDecodeError:
            raise web.HTTPBadRequest(reason="Request body must be valid JSON")
        except pydantic.ValidationError as e:
            raise web.HTTPBadRequest(
                text=e.json(include_context=False, include_url=False),
                content_type="application/json",
            )
        except Exception as e:
            raise web.HTTPBadRequest(reason=str(e))

    def parse_secret_name(self, request: web.Request) -> str:
        name = self.parse_path_part(request, "secret_name")
        self._validate_name(name)
        return name

    def parse_query_param_int(self, request: web.Request, name: str, min_: int | None, max_: int | None) -> int | None:
        value_str = request.query.get(name)
        if not value_str:
            return None
        try:
            value = int(value_str)
        except ValueError:
            raise web.HTTPBadRequest(reason=f"Query param {name!r} must be an integer")
        if min_ is not None and value < min_:
            raise web.HTTPBadRequest(reason=f"Query param {name!r} can't be less than {min_}")
        if max_ is not None and value > max_:
            raise web.HTTPBadRequest(reason=f"Query param {name!r} can't be greater than {max_}")
        return value

    def parse_version_query_param(self, request: web.Request) -> Optional[int]:
        return self.parse_query_param_int(request, "version", min_=None, max_=None)

    def parse_offset_count_params(self, request: web.Request, max_count: int, default_count: int) -> tuple[int, int]:
        return (
            (self.parse_query_param_int(request, "offset", min_=0, max_=None) or 0),
            (self.parse_query_param_int(request, "count", min_=0, max_=max_count) or default_count),
        )

    def parse_query_param_bool(self, request: web.Request, name: str, default: bool) -> bool:
        flag = request.query.get(name)
        if flag is None:
            return default
        elif default is True:
            return flag.lower() not in {"false", "0"}
        else:
            return flag.lower() in {"true", "1"}

    # endregion

    # region: bot helpers
    # common tasks with bots / related data

    async def load_bot_config(self, username: str, bot_id: str, version: BotVersion) -> BotConfig:
        config = await self.store.load_bot_config(username, bot_id, version)
        if config is None:
            raise web.HTTPNotFound(reason=f"Bot not found: {bot_id!r}")
        return config

    async def _make_bare_bot(self, username: str, bot_id: str) -> AsyncTeleBot:
        return await make_bare_bot(
            username,
            bot_config=await self.load_bot_config(username, bot_id, version=-1),
            secret_store=self.secret_store,
            _bot_factory=self._bot_factory,
        )

    async def _construct_bot(self, username: str, bot_id: str, bot_config: BotConfig) -> BotRunner:
        return await construct_bot(
            username=username,
            bot_id=bot_id,
            bot_config=bot_config,
            secret_store=self.secret_store,
            form_results_store=self.store.form_results.adapter_for(
                username=username,
                bot_id=bot_id,
            ),
            metrics_store=self.store.metrics,
            redis=self.redis,
            group_chat_discovery_handler=self.group_chat_discovery_handler,
            _bot_factory=self._bot_factory,
        )

    def _log_prefix(self, username: str, bot_id: str, version: BotVersion | None = None) -> str:
        prefix = f"[{username}][{bot_id}]"
        if version is not None:
            prefix += f"[v{version}]"
        return prefix

    async def stop_bot(self, username: str, bot_id: str) -> bool:
        log_prefix = self._log_prefix(username, bot_id)
        if await self.runner.stop(username, bot_id):
            logger.info(f"{log_prefix} Stopped bot")
            await self.store.set_bot_not_running(username, bot_id)
            await self.store.save_event(username, bot_id, event=BotStoppedEvent(username=username, event="stopped"))
            return True
        else:
            logger.info(f"{log_prefix} Bot is not running")
            return False

    async def start_bot(
        self,
        username: str,
        bot_id: str,
        version: BotVersion,
    ) -> None:
        """Start a specific version of the bot; this method should be initiated by a user"""
        bot_config = await self.load_bot_config(username, bot_id, version)
        log_prefix = self._log_prefix(username, bot_id, version)
        logger.info(f"{log_prefix} (Re)starting bot")
        await self.stop_bot(username, bot_id)
        try:
            bot_runner = await self._construct_bot(
                username=username,
                bot_id=bot_id,
                bot_config=bot_config,
            )
        except Exception as e:
            logger.exception(f"{log_prefix} Error constructing bot")
            await self.store.set_bot_not_running(username, bot_id)
            raise web.HTTPBadRequest(reason=str(e))
        if not await self.runner.start(username=username, bot_id=bot_id, bot_runner=bot_runner):
            await self.store.set_bot_not_running(username, bot_id)
            logger.error(f"{log_prefix} Bot failed to start")
            raise web.HTTPInternalServerError(reason="Failed to start bot")
        logger.info(f"{log_prefix} Bot started OK!")
        await self.store.set_bot_running_version(username, bot_id, version=version)
        await self.store.save_event(
            username,
            bot_id,
            event=BotStartedEvent(
                username=username,
                event="started",
                version=version,
            ),
        )

    # region: API endpoints

    async def create_constructor_web_app(self) -> web.Application:
        app = web.Application()
        routes = web.RouteTableDef()

        ##################################################################################
        # region secrets API

        @routes.post("/api/secrets/{secret_name}")
        async def upsert_secret(request: web.Request) -> web.Response:
            """
            ---
            description: Create or update secret
            responses:
                "201":
                    description: Success
            """
            username = await self.authenticate(request)
            secret_name = self.parse_secret_name(request)
            secret_value = await request.text()
            if not secret_value:
                raise web.HTTPBadRequest(reason="Secret can't be empty")
            result = await self.secret_store.save_secret(
                secret_name=secret_name,
                secret_value=secret_value,
                owner_id=username,
                allow_update=True,
            )
            return web.Response(text=result.message, status=200 if result.is_saved else 400)

        @routes.delete("/api/secrets/{secret_name}")
        async def delete_secret(request: web.Request) -> web.Response:
            """
            ---
            description: Delete secret
            responses:
                "201":
                    description: Success
            """
            username = await self.authenticate(request)
            secret_name = self.parse_secret_name(request)
            if await self.secret_store.remove_secret(
                secret_name=secret_name,
                owner_id=username,
            ):
                return web.Response(text="Removed", status=200)
            else:
                return web.Response(text="Secret not found", status=404)

        @routes.get("/api/secrets")
        async def list_secret_names(request: web.Request) -> web.Response:
            """
            ---
            description: List available secret names
            produces:
            - application/json
            responses:
                "201":
                    description: List of string secret names
            """
            username = await self.authenticate(request)
            secret_names = await self.secret_store.list_secrets(owner_id=username)
            return web.json_response(data=secret_names)

        # endregion
        ##################################################################################
        # region configs CRUD

        @routes.post("/api/config/{bot_id}")
        async def save_new_bot_config_version(request: web.Request) -> web.Response:
            """
            ---
            description: Create or update bot configuration
            produces:
            - application/json
            responses:
                "201":
                    description: New bot is created, config is echoed back
                "200":
                    description: Bot config is updated, the old version of config is returned
            """
            username = await self.authenticate(request)
            bot_id = self.parse_bot_id(request)
            existing_bot_config = await self.store.load_bot_config(username, bot_id)
            payload = await self.parse_body_as_model(request, SaveBotConfigVersionPayload)
            await self.store.save_bot_config(
                username,
                bot_id,
                config=payload.config,
                meta=BotConfigVersionMetadata(message=payload.version_message),
            )

            new_bot_version_count = await self.store.bot_config_version_count(username, bot_id)
            new_version = new_bot_version_count - 1  # i.e. the last one
            await self.store.save_event(
                username,
                bot_id,
                event=BotEditedEvent(
                    username=username,
                    event="edited",
                    new_version=new_version,
                ),
            )

            if payload.display_name is not None:
                await self.store.save_bot_display_name(username, bot_id, payload.display_name)

            if payload.start:
                await self.start_bot(username, bot_id, version=new_version)

            if existing_bot_config is None:
                return web.json_response(text=payload.config.model_dump_json(), status=201)
            else:
                return web.json_response(text=existing_bot_config.model_dump_json())

        @routes.get("/api/config/{bot_id}")
        async def get_bot_config(request: web.Request) -> web.Response:
            """
            ---
            description: Get config for bot with a given name
            produces:
            - application/json
            responses:
                "200":
                    description: OK
                "404":
                    description: No config found
            """
            username = await self.authenticate(request)
            bot_id = self.parse_bot_id(request)
            version = self.parse_version_query_param(request)
            config = await self.load_bot_config(
                username,
                bot_id,
                version=version if version is not None else -1,
            )

            # HACK: on query apram flag - emulate legacy behaviour where display name was stored inside bot config
            # to be removed
            if "with_display_name" in request.query:
                config.display_name = await self.store.load_bot_display_name(username, bot_id)
            return web.json_response(text=config.model_dump_json())

        @routes.delete("/api/config/{bot_id}")
        async def remove_bot_config(request: web.Request) -> web.Response:
            """
            ---
            description: Delete bot config; if the bot was running, it is stopped
            produces:
            - application/json
            responses:
                "200":
                    description: Deleted bot config
            """
            username = await self.authenticate(request)
            bot_id = self.parse_bot_id(request)
            config = await self.load_bot_config(username, bot_id, version=-1)
            await self.stop_bot(username, bot_id)
            await self.store.remove_bot_config(username, bot_id)
            await self.secret_store.remove_secret(config.token_secret_name, owner_id=username)
            await self.store.save_event(
                username,
                bot_id,
                BotDeletedEvent(username=username, event="deleted"),
            )
            return web.json_response(text=config.model_dump_json())

        # endregion
        ##################################################################################
        # region bot lifecycle
        # starting and stopping bots

        @routes.post("/api/start/{bot_id}")
        async def start_bot(request: web.Request) -> web.Response:
            """
            ---
            description: Start bot
            produces:
            - text/plain
            responses:
                "201":
                    description: Bot started
                "200":
                    description: Bot is already running
            """
            username = await self.authenticate(request)
            bot_id = self.parse_bot_id(request)
            payload = await self.parse_body_as_model(request, StartBotPayload)
            await self.start_bot(username, bot_id, version=payload.version)
            return web.Response(text="OK", status=201)

        @routes.post("/api/stop/{bot_id}")
        async def stop_bot(request: web.Request) -> web.Response:
            """
            ---
            description: Stop bot
            produces:
            - text/plain
            responses:
                "201":
                    description: Bot stopped
                "200":
                    description: Bot was not running
            """
            username = await self.authenticate(request)
            bot_id = self.parse_bot_id(request)
            if await self.stop_bot(username, bot_id):
                return web.Response(text="Bot stopped")
            else:
                return web.Response(text="Bot was not running")

        # endregion
        ##################################################################################
        # region bot info
        # name, running status, history, etc

        @routes.put("/api/display-name/{bot_id}")
        async def update_bot_display_name(request: web.Request) -> web.Response:
            """
            ---
            description: Update bot's display name, i.e. the one used in constructor web UI.
            produces:
            - application/json
            responses:
                "200":
                    description: Name changed OK
                "404":
                    description: Bot name does not exist
            """
            username = await self.authenticate(request)
            bot_id = self.parse_bot_id(request)
            payload = await self.parse_body_as_model(request, UpdateBotDisplayNamePayload)
            if not await self.store.is_bot_exists(username, bot_id):
                raise web.HTTPNotFound(reason="Bot id not found")
            if await self.store.save_bot_display_name(username, bot_id, payload.display_name):
                return web.Response()
            else:
                raise web.HTTPInternalServerError(reason="Failed to save bot display name")

        @routes.get("/api/info/{bot_id}")
        async def get_bot_info(request: web.Request) -> web.Response:
            """
            ---
            description: Get info for bot with a given name
            produces:
            - application/json
            responses:
                "200":
                    description: OK
                "404":
                    description: No config found
            """
            username = await self.authenticate(request)
            bot_id = self.parse_bot_id(request)
            info = await self.store.load_bot_info(
                username,
                bot_id,
                detailed=self.parse_query_param_bool(request, "detailed", default=True),
            )
            if info is None:
                raise web.HTTPNotFound(reason="Bot id not found")
            else:
                return web.json_response(text=info.model_dump_json())

        @routes.get("/api/info")
        async def list_bot_infos(request: web.Request) -> web.Response:
            """
            ---
            description: List all bots with general info about running status, recent actions, etc
            produces:
            - application/json
            responses:
                "200":
                    description: List of all bots name and their statuses
            """
            username = await self.authenticate(request)
            bot_ids = await self.store.list_bot_ids(username)
            logger.info(f"Bots owned by {username}: {bot_ids}")
            maybe_bot_infos = [
                await self.store.load_bot_info(
                    username,
                    bot_id,
                    detailed=self.parse_query_param_bool(request, "detailed", default=True),
                )
                for bot_id in bot_ids
            ]
            bot_infos = [bi for bi in maybe_bot_infos if bi is not None]
            if len(maybe_bot_infos) != len(bot_infos):
                missing_info_bot_ids = [bot_id for bot_id, info in zip(bot_ids, maybe_bot_infos) if info is None]
                logger.error(
                    "Failed to construct bot infos for some of the user's bots, will ignore them: "
                    + f"{missing_info_bot_ids}"
                )
            return web.json_response(body=BotInfoList.dump_json(bot_infos))

        @routes.get("/api/info/{bot_id}/versions")
        async def get_bot_versions_page(request: web.Request) -> web.Response:
            username = await self.authenticate(request)
            bot_id = self.parse_bot_id(request)
            offset, count = self.parse_offset_count_params(request, max_count=100, default_count=20)
            bot_info = await self.store.load_bot_info(username, bot_id, detailed=False)
            if bot_info:
                start, end = page_params_to_redis_indices(offset, count)
                return web.json_response(
                    text=BotVersionsPage(
                        bot_info=bot_info,
                        versions=await self.store.load_version_info(
                            username, bot_id, start_version=start, end_version=end
                        ),
                        total_versions=await self.store.bot_config_version_count(username, bot_id),
                    ).model_dump_json()
                )
            else:
                raise web.HTTPNotFound(reason="Bot id not found")

        # endregion
        ##################################################################################
        # region form results

        @routes.get("/api/forms/{bot_id}/{form_block_id}/responses")
        async def get_form_responses_page(request: web.Request) -> web.Response:
            """
            ---
            description: Get form responses
            produces:
            - application/json
            responses:
                "200":
                    description: OK
            """
            username = await self.authenticate(request)
            bot_id = self.parse_bot_id(request)
            global_form_id = GlobalFormId(
                username=username,
                bot_id=bot_id,
                form_block_id=self.parse_path_part(request, "form_block_id"),
            )
            offset, count = self.parse_offset_count_params(request, max_count=100, default_count=20)
            bot_info = await self.store.load_bot_info(username=username, bot_id=bot_id, detailed=False)
            if not bot_info:
                raise web.HTTPNotFound(reason="Bot not found")
            form_info = await self.store.form_results.load_form_info(global_form_id)
            if not form_info:
                raise web.HTTPNotFound(reason="Form not found")
            form_results = await self.store.form_results.load_page(global_form_id, offset=offset, count=count)
            return web.json_response(
                text=FormResultsPage(bot_info=bot_info, info=form_info, results=form_results).model_dump_json(),
            )

        @routes.get("/api/forms/{bot_id}/{form_block_id}/export")
        async def export_form_responses_as_csv(request: web.Request) -> web.StreamResponse:
            """
            ---
            description: Export form responses in a CSV format
            produces:
            - text/csv
            responses:
                "200":
                    description: OK
            """
            username = await self.authenticate(request)
            bot_id = self.parse_bot_id(request)
            global_form_id = GlobalFormId(
                username=username, bot_id=bot_id, form_block_id=self.parse_path_part(request, "form_block_id")
            )
            filter = FormResultsFilter(
                min_timestamp=self.parse_query_param_int(request, name="min_timestamp", min_=None, max_=None),
                max_timestamp=self.parse_query_param_int(request, name="max_timestamp", min_=None, max_=None),
            )
            with_header = self.parse_query_param_bool(request, "header", default=True)
            form_info = await self.store.form_results.load_form_info(global_form_id)
            if not form_info:
                raise web.HTTPNotFound(reason="Form not found")
            MAX_RESULTS_COUNT = 1000
            results, is_full = await self.store.form_results.load(
                form_id=global_form_id,
                filter=filter,
                load_page_size=100,
                max_results_count=MAX_RESULTS_COUNT,
            )
            csv_out_stream = StringIO()
            csv_writer = csv.DictWriter(
                f=csv_out_stream,
                fieldnames=[TIMESTAMP_KEY, USER_KEY] + list(form_info.field_names.keys()),
            )
            if with_header:
                header = {TIMESTAMP_KEY: "Timestamp", USER_KEY: "User", **form_info.field_names}
                csv_writer.writerow(header)
            for r in results:
                if TIMESTAMP_KEY in r:
                    timestamp = r.get(TIMESTAMP_KEY)
                    if isinstance(timestamp, float):
                        r[TIMESTAMP_KEY] = datetime.datetime.fromtimestamp(timestamp).isoformat()
                csv_writer.writerow(r)
            return web.Response(
                status=200 if is_full else 206,
                text=csv_out_stream.getvalue(),
                content_type="text/csv",
                headers={
                    hdrs.CONTENT_DISPOSITION: (
                        f"attachment; filename=\"Results for {form_info.title or 'Unnamed form'} "
                        + f"({filter.describe()}; generated on "
                        + f'{datetime.datetime.now().isoformat(timespec='minutes')}).csv"'
                    ),
                },
            )

        @routes.put("/api/forms/{bot_id}/{form_block_id}/title")
        async def update_form_title(request: web.Request) -> web.Response:
            """
            ---
            description: Update form title
            produces:
            - application/json
            responses:
                "200":
                    description: OK
            """
            username = await self.authenticate(request)
            form_id = GlobalFormId(
                username=username,
                bot_id=self.parse_bot_id(request),
                form_block_id=self.parse_path_part(request, "form_block_id"),
            )
            new_title = await request.text()
            if len(new_title) > 512:
                raise web.HTTPBadRequest(reason="The title is too long")
            if await self.store.form_results.save_form_title(form_id, title=new_title):
                return web.Response()
            else:
                return web.HTTPInternalServerError(reason="Unable to save new form title")

        # endregion
        ##################################################################################
        # region bot metrics and errors

        @routes.get("/api/errors/{bot_id}")
        async def get_bot_errors(request: web.Request) -> web.Response:
            """
            ---
            description: Get form responses
            produces:
            - application/json
            responses:
                "200":
                    description: OK
            """
            username = await self.authenticate(request)
            bot_id = self.parse_bot_id(request, "bot_id")
            offset, count = self.parse_offset_count_params(request, max_count=100, default_count=20)
            errors = await self.store.metrics.load_errors(username, bot_id, offset, count)
            return web.json_response(text=BotErrorsPage(errors=errors).model_dump_json())

        # endregion
        ##################################################################################
        # region validation

        @routes.post("/api/validate-token")
        async def validate_bot_token(request: web.Request) -> web.Response:
            """
            ---
            description: Validate Telegram bot token
            produces:
            - application/json
            responses:
                "200":
                    description: OK
                "400":
                    description: Invalid token (with forwarded Telegram bot API response)
            """
            _ = await self.authenticate(request)
            token_payload = await self.parse_body_as_model(request, BotTokenPayload)
            try:
                await AsyncTeleBot(token=token_payload.token).get_me()
            except Exception as e:
                raise web.HTTPBadRequest(reason=f"Bot token validation failed ({e})")
            return web.Response(text="Token is valid")

        # endregion
        ##################################################################################
        # region sync w/ telegram
        # retrieving up-to-date data from Telegram or sending updates to them

        @routes.get("/api/bot-user/{bot_id}")
        async def get_bot_user(request: web.Request) -> web.Response:
            """
            ---
            description: Retrieve info about bot account (username, name, settings, ...)
            produces:
            - application/json
            responses:
                "200":
                    description: TgBotUser object
            """
            username = await self.authenticate(request)
            bot_id = self.parse_bot_id(request)
            bot = await self._make_bare_bot(username, bot_id)
            try:
                tg_bot_user = await TgBotUser.fetch(bot, telegram_files_downloader=self.telegram_files_downloader)
                return web.json_response(tg_bot_user.model_dump())
            except Exception:
                logger.exception("Unexpected error retrieving tg bot user info")
                raise web.HTTPInternalServerError(reason="Failed to retrieve bot user details")

        @routes.put("/api/bot-user/{bot_id}")
        async def update_bot_user(request: web.Request) -> web.Response:
            """
            ---
            description: Update bot info (name, description and short descrition)
            produces:
            - application/json
            responses:
                "200":
                    description: OK
            """
            username = await self.authenticate(request)
            bot_id = self.parse_bot_id(request)
            bot_user_update = await self.parse_body_as_model(request, TgBotUserUpdate)
            if not bot_user_update.name:
                raise web.HTTPBadRequest(reason="Bot name can't be empty")
            bot = await self._make_bare_bot(username, bot_id)
            try:
                await bot_user_update.save(bot, telegram_files_downloader=self.telegram_files_downloader)
                return web.Response(reason="OK")
            except Exception:
                logger.exception("Error updating bot user info")
                raise web.HTTPInternalServerError(reason="Error updating bot detailed information")

        @routes.post("/api/start-group-chat-discovery/{bot_id}")
        async def start_discovering_group_chats(request: web.Request) -> web.Response:
            """
            ---
            description: |
                Start "group discovery" mode. For running bot it means just adding a few handlers,
                otherwise a stub bot is run.
            produces:
            - application/json
            responses:
                "200":
                    description: OK
            """
            username = await self.authenticate(request)
            bot_id = self.parse_bot_id(request)
            if not await self.store.is_bot_running(username, bot_id):
                logger.info("Group discovery mode requested but bot is not running, starting stub bot")
                await self.start_bot(username, bot_id, version="stub")
            await self.group_chat_discovery_handler.start_discovery(username, bot_id)
            return web.Response(text="Group discovery started")

        @routes.post("/api/stop-group-chat-discovery/{bot_id}")
        async def stop_discovering_group_chats(request: web.Request) -> web.Response:
            """
            ---
            description: Stop "group discovery" mode. If a stub bot was used it is stopped.
            produces:
            - application/json
            responses:
                "200":
                    description: OK
            """
            username = await self.authenticate(request)
            bot_id = self.parse_bot_id(request)
            await self.group_chat_discovery_handler.stop_discovery(username, bot_id)
            if await self.store.get_bot_running_version(username, bot_id) == "stub":
                logger.info("Group discovery mode stopped and bot stub was running, stopping it")
                await self.stop_bot(username, bot_id)
            return web.Response(text="Group discovery stopped")

        @routes.get("/api/available-group-chats/{bot_id}")
        async def get_available_group_chats(request: web.Request) -> web.Response:
            """
            ---
            description: Get discovered and validated chats currently available to the bot
            produces:
            - application/json
            responses:
                "200":
                    description: List of TgGroupChat objects
            """
            username = await self.authenticate(request)
            bot_id = self.parse_bot_id(request)
            chats = await self.group_chat_discovery_handler.validate_discovered_chats(
                username,
                bot_id,
                bot=await self._make_bare_bot(username, bot_id),
            )
            # this is probably not chronological or anything, but at least it's consistent...
            chats.sort(key=lambda c: c.id)
            return web.json_response(data=[chat.model_dump(mode="json") for chat in chats])

        @routes.get("/api/group-chat/{bot_id}")
        async def get_group_chat(request: web.Request) -> web.Response:
            """
            ---
            description: Retrieve info about a group chat available to bot
            produces:
            - application/json
            responses:
                "200":
                    description: TgGroupChat object
                "404":
                    description: Chat not found
            """
            username = await self.authenticate(request)
            bot_id = self.parse_bot_id(request)
            bot = await self._make_bare_bot(username, bot_id)
            # NOTE: numeric chat ids are not casted into ints because it doesn't matter for Telegram bot API
            group_chat_id = request.query.get("group_chat")
            if group_chat_id is None:
                raise web.HTTPBadRequest(reason="group_chat query param expected")
            chat = await self.group_chat_discovery_handler.get_group_chat(bot=bot, chat_id=group_chat_id)
            if chat is None:
                raise web.HTTPNotFound(reason="Chat does not exist or is not available to the bot")
            else:
                return web.json_response(data=chat.model_dump(mode="json"))

        # endregion
        ##################################################################################
        # region static content

        @routes.get("/api/all-languages")
        async def all_languages(request: web.Request) -> web.Response:
            """
            ---
            description: List all available languages with code, name and emoji, if exists
            produces:
            - application/json
            responses:
                "200":
                    description: List of Language objects
            """
            await self.authenticate(request)
            return web.json_response(
                data=[
                    {
                        "code": lang.code,
                        "name": lang.name,
                        "emoji": lang.emoji,
                    }
                    for lang in LanguageData.all().values()
                ]
            )

        @routes.get("/api/prefilled-messages")
        async def prefilled_messages(request: web.Request) -> web.Response:
            """
            ---
            description: List all available languages with code, name and emoji, if exists
            produces:
            - application/json
            responses:
                "200":
                    description: List of Language objects
            """
            await self.authenticate(request)
            return web.Response(body=get_prefilled_messages(), content_type="application/json")

        @routes.get("/api/logged-in-user")
        async def get_logged_in_user(request: web.Request) -> web.Response:
            """
            ---
            description: Get logged in user with auth-specific details
            produces:
            - application/json
            responses:
                "200":
                    description: LoggedInUser object
            """
            user = await self._authenticate_full(request)
            return web.Response(
                body=user.model_dump_json(),
                content_type="application/json",
            )

        @routes.get("/")
        @routes.get("")
        async def landing_page(request: web.Request) -> web.Response:
            return web.Response(
                body=static_file_content(self.static_files_dir / "landing.html"),
                content_type="text/html",
            )

        @routes.get("/api/version")
        async def api_version(request: web.Request) -> web.Response:
            return web.Response(text=VERSION or "<unset>")

        STATIC_FILE_GLOBS = ["assets/*", "favicon.ico"]

        @routes.get("/{path:(?!api/).*}")  # mathing all paths except those starting with /api prefix
        async def serve_static_file(request: web.Request) -> web.StreamResponse:
            static_file_path = request.match_info.get("path")
            if static_file_path is None:
                raise web.HTTPNotFound()
            if any(fnmatch.fnmatch(static_file_path, glob) for glob in STATIC_FILE_GLOBS):
                mime_type, _ = mimetypes.guess_type(static_file_path, strict=False)
                return web.Response(
                    body=static_file_content(self.static_files_dir / static_file_path),
                    content_type=mime_type,
                )
            else:
                # if not static file -- must be an app route, so authenticate and serve
                # either login or app page; in the latter case, client-side routing kicks
                # in
                username = await self.auth.authenticate_request(request)
                if username is None:
                    return await self.auth.unauthenticated_client_response(
                        request, static_files_dir=self.static_files_dir
                    )
                return web.Response(
                    body=static_file_content(self.static_files_dir / "index.html"),
                    content_type="text/html",
                )

        # endregion
        ##################################################################################

        app.add_routes(routes)
        await self.auth.setup_routes(app)
        setup_swagger(app=app, swagger_url="/api/swagger")
        setup_cors(app)
        setup_debugging(app)
        return app

    # endregion

    # region constructor lifecycle

    def start_stored_bots_in_background(self) -> None:
        async def _start_stored_bots() -> None:
            logger.info("Starting stored bots...")
            total_bots = 0
            started_bots = 0
            async for username, bot_id, version in self.store.iter_running_bot_versions():
                total_bots += 1
                log_prefix = self._log_prefix(username, bot_id, version)
                logger.debug(f"{log_prefix} Starting stored bot (#{total_bots})")
                try:
                    bot_config = await self.store.load_bot_config(username, bot_id, version)
                    if bot_config is None:
                        raise RuntimeError("Bot is marked as running bot no config found")
                    bot_runner = await self._construct_bot(username, bot_id, bot_config)
                    if not await self.runner.start(username=username, bot_id=bot_id, bot_runner=bot_runner):
                        raise RuntimeError(f"Runner {self.runner} refused to start the bot, maybe see error above")
                    started_bots += 1
                except Exception:
                    logger.exception(f"{log_prefix} Error starting stored bot, will mark it as not running")
                    try:
                        await self.store.set_bot_not_running(username, bot_id)
                    except Exception:
                        logger.exception(f"{log_prefix} Failed to mark bot as non-running after failed startup")
            logger.info(f"Started {started_bots}/{total_bots} bots in total")

        self._start_stored_bots_task = create_error_logging_task(_start_stored_bots(), name="Start stored bots")

    async def setup(self) -> None:
        self.start_stored_bots_in_background()
        auth_bot_runner = await self.auth.setup_bot()
        if auth_bot_runner is not None:
            logger.info("Starting auth bot")
            await self.runner.start(username="internal", bot_id="auth-bot", bot_runner=auth_bot_runner)
        await self.telegram_files_downloader.setup()

    async def cleanup(self) -> None:
        logger.info("Cleanup started")
        await self.telegram_files_downloader.cleanup()
        await self.runner.cleanup()
        # await telebot.api.session_manager.close_session()
        logger.info("Cleanup completed")

    # public methods to run constructor in different scenarios

    async def run_polling(self, port: int) -> None:
        """Standalone run, polling is used to get updates from Telegram API"""
        logger.info("Running telebot constructor with polling")
        self._runner = PollingConstructedBotRunner()
        await self.setup()
        constructor_web_app = await self.create_constructor_web_app()
        if BASE_PATH:
            logger.info(f"Constructor web app is scoped under path {BASE_PATH}")
            app = web.Application()
            app.add_subapp(BASE_PATH, constructor_web_app)
        else:
            app = constructor_web_app
        aiohttp_runner = web.AppRunner(app)
        await aiohttp_runner.setup()
        site = web.TCPSite(aiohttp_runner, "0.0.0.0", port)
        logger.info(f"Running server on {site.name}")
        try:
            await site.start()
            while True:
                await asyncio.sleep(3600)
        finally:
            await aiohttp_runner.cleanup()
            await self.cleanup()

    async def setup_on_webhook_app(self, webhook_app: WebhookApp) -> None:
        """Run constructor app as part of larger application, represented by a WebhookApp instance"""
        logger.info(f"Setting up telebot constructor web app on webhook app with base URL {webhook_app.base_url!r}")
        # create constructor web app *before* setting up any bots as it adds routes to aiohttp app
        tbc_aiohttp_app = await self.create_constructor_web_app()
        tbc_aiohttp_app.on_cleanup.append(lambda _: self.cleanup())
        if BASE_PATH:
            logger.info(f"Constructor web app is scoped under {BASE_PATH!r}")
            webhook_app.aiohttp_app.add_subapp(BASE_PATH, tbc_aiohttp_app)
        else:
            logger.warning(
                "No base path configured at build time, so we're replacing webhook app entirely "
                + "and effectively deleting all previously set webhooks"
            )
            webhook_app.aiohttp_app = tbc_aiohttp_app

        self._runner = WebhookAppConstructedBotRunner(webhook_app)
        await self.setup()

    # endregion
