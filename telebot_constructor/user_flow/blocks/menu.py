import dataclasses
from typing import Any, Optional

from pydantic import BaseModel
from telebot_components.menu.menu import Menu as ComponentsMenu
from telebot_components.menu.menu import MenuConfig as ComponentsMenuConfig
from telebot_components.menu.menu import MenuHandler
from telebot_components.menu.menu import MenuItem as ComponentsMenuItem
from telebot_components.menu.menu import (
    MenuMechanism,
    TerminatorContext,
    TerminatorResult,
)

from telebot_constructor.user_flow.blocks.base import UserFlowBlock
from telebot_constructor.user_flow.types import (
    SetupResult,
    UserFlowContext,
    UserFlowSetupContext,
)
from telebot_constructor.utils.pydantic import (
    ExactlyOneNonNullFieldModel,
    LocalizableText,
)


class MenuItem(ExactlyOneNonNullFieldModel):
    label: LocalizableText

    # exactly one field must be non-None
    submenu: Optional["Menu"] = None
    next_block_id: Optional[str] = None  # for terminal items
    link_url: Optional[str] = None  # for link buttons (works only if mechanism is inline)

    def to_components_menu_item(self, global_config: ComponentsMenuConfig) -> ComponentsMenuItem:
        return ComponentsMenuItem(
            label=self.label,
            submenu=None if self.submenu is None else self.submenu.to_components_menu(global_config),
            terminator=self.next_block_id,
            link_url=self.link_url,
            bound_category=None,
        )


class Menu(BaseModel):
    text: LocalizableText
    no_back_button: bool
    items: list[MenuItem]

    def to_components_menu(self, global_config: ComponentsMenuConfig) -> ComponentsMenu:
        config_override = {"back_label": None} if self.no_back_button else {}
        config = dataclasses.replace(global_config, **config_override)  # type: ignore
        return ComponentsMenu(
            text=self.text,
            menu_items=[item.to_components_menu_item(global_config) for item in self.items],
            config=config,
        )


class MenuConfig(BaseModel):
    back_label: LocalizableText
    mechanism: MenuMechanism
    lock_after_termination: bool


class MenuBlock(UserFlowBlock):
    """Multilevel menu block powered by Telegram inline buttons"""

    menu: Menu
    config: MenuConfig

    def model_post_init(self, __context: Any) -> None:
        self._components_config = ComponentsMenuConfig(
            back_label=self.config.back_label,
            lock_after_termination=self.config.lock_after_termination,
            # TODO: convert markdown and plain texts to HTML and set is_text_html to True
            is_text_html=False,
            mechanism=self.config.mechanism,
        )
        self._components_menu = self.menu.to_components_menu(global_config=self._components_config)

    @property
    def menu_handler(self) -> MenuHandler:
        if self._components_menu_handler is None:
            raise RuntimeError("self.menu_handler called before setup method")
        return self._components_menu_handler

    async def enter(self, context: UserFlowContext) -> None:
        await self.menu_handler.start_menu(bot=context.bot, user=context.user)

    async def setup(self, context: UserFlowSetupContext) -> SetupResult:
        self._components_menu_handler = MenuHandler(
            name=self.block_id,
            bot_prefix=context.bot_prefix,
            menu_tree=self._components_menu,
            redis=context.redis,
            category_store=None,
            language_store=context.language_store,
        )

        async def on_terminal_menu_option_selected(terminator_context: TerminatorContext) -> Optional[TerminatorResult]:
            next_block_id = terminator_context.terminator
            await context.enter_block(
                next_block_id,
                UserFlowContext.from_setup_context(
                    setup_ctx=context,
                    chat=terminator_context.menu_message.chat if terminator_context.menu_message is not None else None,
                    user=terminator_context.user,
                    last_update_content=terminator_context.menu_message,
                ),
            )
            return None

        self.menu_handler.setup(
            bot=context.bot,
            on_terminal_menu_option_selected=on_terminal_menu_option_selected,
        )
        return SetupResult.empty()
