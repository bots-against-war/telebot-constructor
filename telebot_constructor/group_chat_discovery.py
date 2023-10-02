import datetime
import logging
from typing import Union

from telebot import AsyncTeleBot
from telebot import types as tg
from telebot.types import constants as tg_const
from telebot_components.redis_utils.interface import RedisInterface
from telebot_components.stores.generic import KeyFlagStore, KeySetStore

from telebot_constructor.utils import non_capturing_handler
from telebot_constructor.utils.rate_limit_retry import rate_limit_retry

logger = logging.getLogger(__name__)


class GroupChatDiscoveryHandler:
    """
    Service class that encapsulates group chat discovery functionality for bots
    (e.g. to automagically discover admin chats for users)
    """

    STORE_PREFIX = "telebot-constructor-group-chat-discovery"

    def __init__(self, redis: RedisInterface) -> None:
        # "{username}-{bot name}" -> flag for group chat discovery mode
        self._bots_in_discovery_mode_store = KeyFlagStore(
            name="bot-in-discovery-mode",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=datetime.timedelta(minutes=10),
        )
        # "{username}-{bot name}" -> set of discovered group chat ids
        self._available_group_chat_ids = KeySetStore[Union[str, int]](
            name="available-group-chat-ids",
            prefix=self.STORE_PREFIX,
            redis=redis,
            expiration_time=None,
            dumper=str,
            loader=int,
        )

    def _full_key(self, username: str, bot_name: str) -> str:
        return f"{username}-{bot_name}"

    async def start_group_chat_discovery_mode(self, username: str, bot_name: str) -> None:
        await self._bots_in_discovery_mode_store.set_flag(self._full_key(username, bot_name))

    async def is_discovering_group_chats(self, username: str, bot_name: str) -> bool:
        return await self._bots_in_discovery_mode_store.is_flag_set(self._full_key(username, bot_name))

    async def save_discovered_chat(self, username: str, bot_name: str, chat_id: Union[str, int]) -> None:
        await self._available_group_chat_ids.add(self._full_key(username, bot_name), chat_id)

    async def validate_discovered_chats(self, username: str, bot_name: str, bot: AsyncTeleBot) -> list[tg.Chat]:
        """
        Check saved available chats and validate they are still available to the bot (i.e. it was not kicked, group chat
        was not promoted to supergroup, etc); return a list of valid chats as telegram Chat objects
        """
        chats: list[tg.Chat] = []
        key = self._full_key(username, bot_name)
        available_chat_ids = await self._available_group_chat_ids.all(key)
        logger.info(
            f"Validating chat ids are available to bot {bot_name!r} (by {username!r}): {sorted(available_chat_ids)}"
        )
        for chat_id in available_chat_ids:
            try:
                async for attempt in rate_limit_retry():
                    with attempt:
                        chat = await bot.get_chat(chat_id)
                chats.append(chat)
            except Exception as e:
                logger.info(f"Found invalid chat id ({e!r}), removing it from available list")
                await self._available_group_chat_ids.remove(key, chat_id)
        return chats

    def setup_handlers(self, username: str, bot_name: str, bot: AsyncTeleBot) -> None:
        @bot.my_chat_member_handler()
        @non_capturing_handler
        async def discover_group_chats_on_add(cmu: tg.ChatMemberUpdated) -> None:
            if (
                tg_const.ChatType(cmu.chat.type) is not tg_const.ChatType.private
                and cmu.new_chat_member.status in {"creator", "administrator", "member", "restricted"}
                and await self.is_discovering_group_chats(username, bot_name)
            ):
                await self.save_discovered_chat(username, bot_name, chat_id=cmu.chat.id)
            if cmu.new_chat_member.status in {"kicked", "left"}:
                await self._available_group_chat_ids.remove(self._full_key(username, bot_name), cmu.chat.id)

        @bot.message_handler(commands=["discover_chat"])
        @non_capturing_handler
        async def discover_group_chat_on_explicit_cmd(message: tg.Message) -> None:
            if tg_const.ChatType(
                message.chat
            ) is not tg_const.ChatType.private and await self.is_discovering_group_chats(username, bot_name):
                await self.save_discovered_chat(username, bot_name, chat_id=message.chat.id)

        @bot.message_handler(commands=["undiscover_chat"])
        @non_capturing_handler
        async def undiscover_group_chat(message: tg.Message) -> None:
            await self._available_group_chat_ids.remove(self._full_key(username, bot_name), message.chat.id)
