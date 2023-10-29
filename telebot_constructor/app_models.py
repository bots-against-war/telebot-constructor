"""Pydantic models for various app endpoints"""
import enum
from typing import Optional

from pydantic import BaseModel
from telebot import AsyncTeleBot
from telebot import types as tg

from telebot_constructor.telegram_files_downloader import TelegramFilesDownloader
from telebot_constructor.utils.rate_limit_retry import rate_limit_retry


class BotTokenPayload(BaseModel):
    token: str


class TgGroupChatType(enum.Enum):
    GROUP = "group"
    SUPERGROUP = "supergroup"
    CHANNEL = "channel"


class TgGroupChat(BaseModel):
    """pydantic projection of https://core.telegram.org/bots/api#chat"""

    id: int
    type: TgGroupChatType
    title: str
    description: Optional[str]
    username: Optional[str]
    is_forum: Optional[bool]
    photo: Optional[str]  # if set, base64-encoded chat photo


class TgBotCommand(BaseModel):
    command: str
    description: str


class TgBotUser(BaseModel):
    """Info on telegram bot, combining info from several Bot API endpoints"""

    id: int

    # as returned by getMe
    username: str

    # as returned by getMyXxx, potentially localizable (we're not using this for now though)
    name: str
    description: str
    short_description: str

    can_join_groups: bool
    can_read_all_group_messages: bool

    commands: list[TgBotCommand]

    userpic: Optional[str]  # base64-encoded bot's avatar photo preview

    @classmethod
    async def fetch(cls, bot: AsyncTeleBot, telegram_files_downloader: TelegramFilesDownloader) -> "TgBotUser":
        """Fetch data from Telegram Bot API and compose TgBotUser object"""
        async for attempt in rate_limit_retry():
            with attempt:
                bot_user = await bot.get_me()
        async for attempt in rate_limit_retry():
            with attempt:
                bot_description = await bot.get_my_description()
        async for attempt in rate_limit_retry():
            with attempt:
                bot_short_description = await bot.get_my_short_description()
        async for attempt in rate_limit_retry():
            with attempt:
                bot_commands_raw = await bot.get_my_commands(scope=None, language_code=None)
                bot_commands = [TgBotCommand(**bc.to_dict()) for bc in bot_commands_raw]
        async for attempt in rate_limit_retry():
            with attempt:
                bot_name_obj = await bot.get_my_name()
                bot_name = bot_name_obj.name if bot_name_obj is not None else None
        async for attempt in rate_limit_retry():
            with attempt:
                bot_user_profile_photos = await bot.get_user_profile_photos(bot_user.id, limit=1)
                bot_userpic_b64: Optional[str] = None
                if bot_user_profile_photos.photos:
                    userpic_photos: list[list[tg.PhotoSize]] = bot_user_profile_photos.photos  # type: ignore
                    bot_userpic_b64 = await telegram_files_downloader.get_base64_file(
                        bot=bot,
                        file_id=min(userpic_photos[0], key=lambda photo_size: photo_size.width).file_id,
                    )
        return TgBotUser(
            id=bot_user.id,
            name=bot_name or bot_user.first_name,
            username=bot_user.username or "",
            description=bot_description.description if bot_description is not None else "",
            short_description=bot_short_description.short_description if bot_short_description is not None else "",
            userpic=bot_userpic_b64,
            commands=bot_commands,
            can_join_groups=bot_user.can_join_groups or False,
            can_read_all_group_messages=bot_user.can_read_all_group_messages or False,
        )


class TgBotUserUpdate(BaseModel):
    name: str
    description: str
    short_description: str

    async def save(self, bot: AsyncTeleBot, telegram_files_downloader: TelegramFilesDownloader) -> None:
        """Upload data stored in the object to Telegram"""
        existing_bot_user = await TgBotUser.fetch(bot, telegram_files_downloader)
        if self.name != existing_bot_user.name:
            async for attempt in rate_limit_retry():
                with attempt:
                    await bot.set_my_name(name=self.name)
        if self.description != existing_bot_user.description:
            async for attempt in rate_limit_retry():
                with attempt:
                    await bot.set_my_description(description=self.description)
        if self.short_description != existing_bot_user.short_description:
            async for attempt in rate_limit_retry():
                with attempt:
                    await bot.set_my_short_description(short_description=self.short_description)


class BotInfo(BaseModel):
    display_name: str
    created_at: str
    last_updated_at: str
    last_run_at: str
    is_running: bool


class BotActionsHistory(BaseModel):
    created_at: str
    last_updated_at: str
    last_run_at: str
    deleted_at: Optional[str]
