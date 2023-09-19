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


class RegexMatchEntryPoint(UserFlowEntryPoint):
    """Entrypoint matching user messages by searching a regex pattern in text"""

    regex: str  # NOTE: re.IGNORECASE flag is used internally
    next_block_id: Optional[UserFlowBlockId]

    def model_post_init(self, __context: Any) -> None:
        self.compiled_regex = re.compile(self.regex, flags=re.IGNORECASE)
        # pattern is considered catch-all if it matches both empty and some non-empty string, e.g.
        # '.*' - catch-all
        # '.+' - not catch-all, rejects empty texts
        # '^$' - not catch-all, rejects non-empty texts
        self.is_catch_all_pattern = bool(self.compiled_regex.search("")) and bool(self.compiled_regex.search("a"))

    def is_catch_all(self) -> bool:
        return self.is_catch_all_pattern

    async def setup(self, context: UserFlowSetupContext) -> SetupResult:
        @context.bot.message_handler(
            # VVVV TODO fix typing in lib to accept Pattern[str]
            regexp=self.compiled_regex,  # type: ignore
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
