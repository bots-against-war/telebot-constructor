from typing import Any, Optional

from pydantic import BaseModel
from telebot_components.language import LanguageChangeContext
from telebot_components.stores.language import (
    LanguageSelectionMenuConfig as ComponentsLanguageSelectionMenuConfig,
)
from telebot_components.stores.language import LanguageStore

from telebot_constructor.user_flow.blocks.base import UserFlowBlock
from telebot_constructor.user_flow.types import (
    SetupResult,
    UserFlowBlockId,
    UserFlowContext,
    UserFlowSetupContext,
)
from telebot_constructor.utils.pydantic import Language, MultilangText


class LanguageSelectionMenuConfig(BaseModel):
    propmt: MultilangText
    is_blocking: bool  # if True, the selector demands a response before going to the next block
    emoji_buttons: bool  # if False, 2-3 letter language code is used instead


class LanguageSelectBlock(UserFlowBlock):
    """
    Language selection menu block. If specified, all texts in the containing user flow must be multilang
    and be translated to all of the supported languages. Only one such block is permitted per user flow.
    """

    menu_config: LanguageSelectionMenuConfig
    supported_languages: list[Language]
    # if not selected AND user's Telegram interface language is not supported, use this
    default_language: Language
    language_selected_next_block_id: Optional[UserFlowBlockId]

    def model_post_init(self, __context: Any) -> None:
        self._setup_result: Optional[SetupResult] = None
        self._language_store: Optional[LanguageStore] = None

    @property
    def language_store(self) -> LanguageStore:
        if self._language_store is None:
            raise RuntimeError("Language selection block was not set up")
        return self._language_store

    async def enter(self, context: UserFlowContext) -> None:
        if self.menu_config.is_blocking:
            await self.language_store.send_reply_keyboard_selector(bot=context.bot, user=context.user)
        else:
            await self.language_store.send_inline_selector(bot=context.bot, user=context.user)

    async def setup(self, context: UserFlowSetupContext) -> SetupResult:
        if self._setup_result is not None:
            return self._setup_result

        self._language_store = LanguageStore(
            redis=context.redis,
            bot_prefix=context.bot_prefix,
            supported_languages=self.supported_languages,
            default_language=self.default_language,
            menu_config=ComponentsLanguageSelectionMenuConfig(
                emojj_buttons=self.menu_config.emoji_buttons,
                select_with_checkmark=True,
                prompt=self.menu_config.propmt,
                is_prompt_html=True,
            ),
        )

        async def on_language_change(lang_change_context: LanguageChangeContext) -> None:
            if self.language_selected_next_block_id is not None:
                await context.enter_block(
                    self.language_selected_next_block_id,
                    UserFlowContext.from_setup_context(
                        setup_ctx=context,
                        chat=None,
                        user=lang_change_context.user,
                        last_update_content=lang_change_context.message,
                    ),
                )

        await self.language_store.setup(bot=context.bot, on_language_change=on_language_change)

        # NOTE: language store setup can be called several times so it's idempotent
        self._setup_result = SetupResult.empty()
        return self._setup_result
