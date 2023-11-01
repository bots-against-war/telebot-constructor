import re
from typing import Any, Optional

from telebot import types as tg

from telebot_constructor.user_flow.entrypoints.base import UserFlowEntryPoint
from telebot_constructor.user_flow.types import (
    SetupResult,
    UserFlowBlockId,
    UserFlowContext,
    UserFlowSetupContext,
)
from telebot_constructor.utils import without_nones


class RegexMatchEntryPoint(UserFlowEntryPoint):
    """Entrypoint matching user messages by searching a regex pattern in text"""

    regex: str  # NOTE: re.IGNORECASE flag is used internally
    next_block_id: Optional[UserFlowBlockId]

    def model_post_init(self, __context: Any) -> None:
        # pattern is considered catch-all if it matches both empty and some non-empty string, e.g.
        # '.*' - catch-all
        # '.+' - not catch-all, rejects empty texts
        # '^$' - not catch-all, rejects non-empty texts
        self._is_catch_all_pattern = bool(re.search(self.regex, "")) and bool(re.search(self.regex, "a"))

    def is_catch_all(self) -> bool:
        return self._is_catch_all_pattern

    async def setup(self, context: UserFlowSetupContext) -> SetupResult:
        @context.bot.message_handler(
            regexp=self.regex,  # type: ignore
            func=context.banned_users_store.not_from_banned_user,
        )
        async def regex_matching_handler(message: tg.Message) -> None:
            if self.next_block_id is not None:
                await context.enter_block(
                    self.next_block_id,
                    UserFlowContext.from_setup_context(
                        setup_ctx=context,
                        chat=message.chat,
                        user=message.from_user,
                        last_update_content=message,
                    ),
                )

        return SetupResult.empty()

    def possible_next_block_ids(self) -> list[str]:
        return without_nones([self.next_block_id])
