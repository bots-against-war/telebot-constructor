import abc
import dataclasses
import logging
from enum import Enum
from typing import Any, Optional, TypeAlias, Union

from pydantic import BaseModel
from telebot import types as tg
from telebot_components.form.field import (
    FormField,
    FormFieldResultFormattingOpts,
    PlainTextField,
    SingleSelectField,
)
from telebot_components.form.form import Form as ComponentsForm
from telebot_components.form.form import FormBranch
from telebot_components.form.handler import FormExitContext as ComponentsFormExitContext
from telebot_components.form.handler import FormHandler as ComponentsFormHandler
from telebot_components.form.handler import (
    FormHandlerConfig as ComponentsFormHandlerConfig,
)

from telebot_constructor.user_flow.blocks.base import UserFlowBlock
from telebot_constructor.user_flow.types import (
    SetupResult,
    UserFlowBlockId,
    UserFlowContext,
    UserFlowSetupContext,
)
from telebot_constructor.utils import AnyChatId, telegram_user_link
from telebot_constructor.utils.pydantic import (
    ExactlyOneNonNullFieldModel,
    LocalizableText,
)

logger = logging.getLogger(__name__)

FormFieldId = str

FormEnd: TypeAlias = None


# region: form fields


class BaseFormFieldConfig(BaseModel, abc.ABC):
    id: FormFieldId
    propmt: LocalizableText
    is_required: bool
    result_formatting_opts: FormFieldResultFormattingOpts

    def base_field_kwargs(self) -> dict[str, Any]:
        return dataclasses.asdict(
            FormField(
                name=self.id,
                required=self.is_required,
                query_message=self.propmt,
                result_formatting_opts=self.result_formatting_opts,
            )
        )

    @abc.abstractmethod
    def construct_field(self) -> FormField:
        ...


class PlainTextFormFieldConfig(BaseFormFieldConfig):
    empty_text_error_msg: LocalizableText

    def construct_field(self) -> PlainTextField:
        return PlainTextField(
            empty_text_error_msg=self.empty_text_error_msg,
            **self.base_field_kwargs(),
        )


EnumDef = dict[str, LocalizableText]


class SingleSelectFormFieldConfig(BaseFormFieldConfig):
    options: EnumDef
    invalid_enum_error_msg: LocalizableText

    def construct_field(self) -> SingleSelectField:
        return SingleSelectField(
            # see https://docs.python.org/3/howto/enum.html#functional-api
            EnumClass=Enum(f"{self.id}-options", self.options),  # type: ignore
            invalid_enum_value_error_msg=self.invalid_enum_error_msg,
            **self.base_field_kwargs(),  # type: ignore
        )


class FormFieldConfig(ExactlyOneNonNullFieldModel):
    plain_text: Optional[PlainTextFormFieldConfig] = None
    single_select: Optional[SingleSelectField] = None

    def specific_config(self) -> BaseFormFieldConfig:
        return self.plain_text or self.single_select  # type: ignore


# endregion


class FormBranchConfig(ExactlyOneNonNullFieldModel):
    members: list["BranchingFormMemberConfig"]
    condition_match_value: Optional[str] = None

    def constuct_branch(self) -> FormBranch:
        return FormBranch(
            members=[m.construct_member() for m in self.members],
            condition=self.condition_match_value,  # type: ignore
        )


class BranchingFormMemberConfig(ExactlyOneNonNullFieldModel):
    field: Optional[FormFieldConfig] = None
    branch: Optional[FormBranchConfig] = None

    def construct_member(self) -> Union[FormField, FormBranch]:
        if self.field is not None:
            return self.field.specific_config().construct_field()
        elif self.branch is not None:
            return self.branch.constuct_branch()
        else:
            raise RuntimeError("All fields in exactly one non null field model are None")


class FormMessages(BaseModel):
    form_start: LocalizableText
    field_is_skippable: LocalizableText
    field_is_not_skippable: LocalizableText
    please_enter_correct_value: LocalizableText
    unsupported_command: LocalizableText
    cancelling_because_of_error: LocalizableText


class FormResultsExportToChatConfig(BaseModel):
    chat_id: AnyChatId
    via_feedback_handler: bool


class FormResultsExportConfig(BaseModel):
    is_anonymous: bool
    to_chat: Optional[FormResultsExportToChatConfig]


def _validate_template(template: LocalizableText, placeholder_count: int, title: str) -> LocalizableText:
    def _validate_string(template_str: str, subtitle: Optional[str]) -> str:
        actual_placeholder_count = template_str.count(r"{}")
        if actual_placeholder_count != placeholder_count:
            full_title = title
            if subtitle:
                full_title += f" ({subtitle})"
            raise ValueError(
                f'Expected {placeholder_count} "{{}}" placeholders in {full_title}, found {actual_placeholder_count}'
            )
        return template_str

    if isinstance(template, str):
        return _validate_string(template, subtitle=None)
    else:
        return {lang: _validate_string(localization, subtitle=str(lang)) for lang, localization in template.items()}


class FormBlock(UserFlowBlock):
    """
    Block with a series of questions to user with options to export their answers in various formats
    """

    form_name: str
    members: list[BranchingFormMemberConfig]
    messages: FormMessages
    export: FormResultsExportConfig

    form_completed_next_block_id: Optional[UserFlowBlockId]
    form_cancelled_next_block_id: Optional[UserFlowBlockId]

    async def setup(self, context: UserFlowSetupContext) -> SetupResult:
        component_form_members: list[Union[FormField, FormBranch]] = [m.construct_member() for m in self.members]
        self._form = ComponentsForm.branching(component_form_members)

        #                                          VVV impossible to generate type anntation for
        #                                              form result type, so we use Any
        self._form_handler = ComponentsFormHandler[Any](
            redis=context.redis,
            bot_prefix=context.bot_prefix,
            name=self.form_name,
            form=self._form,
            config=ComponentsFormHandlerConfig(
                echo_filled_field=False,
                form_starting_template=_validate_template(
                    self.messages.form_start, placeholder_count=1, title="form start message"
                ),
                can_skip_field_template=_validate_template(
                    self.messages.field_is_skippable, placeholder_count=1, title="field is skippable message"
                ),
                cant_skip_field_msg=_validate_template(
                    self.messages.field_is_not_skippable, placeholder_count=0, title="field is not skippable message"
                ),
                retry_field_msg=_validate_template(
                    self.messages.please_enter_correct_value, placeholder_count=0, title="enter correct value msg"
                ),
                unsupported_cmd_error_template=_validate_template(
                    self.messages.unsupported_command, placeholder_count=1, title="unsupported command message"
                ),
                cancelling_because_of_error_template=_validate_template(
                    self.messages.unsupported_command, placeholder_count=1, title="unsupported cmd message"
                ),
            ),
            language_store=context.language_store,
        )

        def _user_flow_context_for_next_block(form_exit_context: ComponentsFormExitContext) -> UserFlowContext:
            return UserFlowContext.from_setup_context(
                setup_ctx=context,
                chat=(
                    form_exit_context.last_update.chat
                    if isinstance(form_exit_context.last_update, tg.Message)
                    else None
                ),
                user=form_exit_context.last_update.from_user,
                last_update_content=form_exit_context.last_update,
            )

        async def on_form_completed(form_exit_context: ComponentsFormExitContext):
            if self.export.to_chat is not None:
                try:
                    feedback_handler = (
                        context.feedback_handlers.get(self.export.to_chat.chat_id)
                        if self.export.to_chat.via_feedback_handler
                        else None
                    )
                    lang = context.language_store.default_language if context.language_store is not None else None
                    text = self._form.result_to_html(result=form_exit_context.result, lang=lang)
                    if feedback_handler is not None:
                        await feedback_handler.emulate_user_message(
                            bot=context.bot,
                            user=form_exit_context.last_update.from_user,
                            text=text,
                            attachment=None,
                            no_response=True,
                            send_user_identifier_message=self.export.is_anonymous,
                            parse_mode="HTML",
                        )
                    else:
                        if not self.export.is_anonymous:
                            text = telegram_user_link(form_exit_context.last_update.from_user) + "\n\n" + text
                        await context.bot.send_message(
                            chat_id=self.export.to_chat.chat_id,
                            text=text,
                            parse_mode="HTML",
                        )
                except Exception:
                    logger.exception("Error sending form result to admin chat")

            # TODO: more result export options
            # + more export options: Airtable, Google Sheets, Trello
            # + save to internal storage to show in Constructor UI
            if self.form_completed_next_block_id is not None:
                await context.enter_block(
                    self.form_completed_next_block_id,
                    _user_flow_context_for_next_block(form_exit_context),
                )

        async def on_form_cancelled(form_exit_context: ComponentsFormExitContext):
            # TODO: maybe save not completed form in a separate storage?
            if self.form_cancelled_next_block_id is not None:
                await context.enter_block(
                    self.form_cancelled_next_block_id,
                    _user_flow_context_for_next_block(form_exit_context),
                )

        await self._form_handler.setup(
            bot=context.bot,
            on_form_completed=on_form_completed,
            on_form_cancelled=on_form_cancelled,
        )

        # NOTE: not exporting commands like /skip and /cancel because they are only form-specific
        return SetupResult.empty()

    async def enter(self, context: UserFlowContext) -> None:
        await self._form_handler.start(bot=context.bot, user=context.user, initial_form_result=None)
