import abc
import dataclasses
from typing import Any, Optional, TypeAlias, Union

from pydantic import BaseModel
from telebot import types as tg
from telebot_components.form.field import (
    FormField,
    FormFieldResultFormattingOpts,
    NextFieldGetter,
    PlainTextField,
)
from telebot_components.form.form import Form as ComponentsForm
from telebot_components.form.handler import FormExitContext as ComponentsFormExitContext
from telebot_components.form.handler import FormHandler as ComponentsFormHandler
from telebot_components.form.handler import (
    FormHandlerConfig as ComponentsFormHandlerConfig,
)

from telebot_constructor.pydantic_utils import ExactlyOneNonNullFieldModel
from telebot_constructor.user_flow.blocks.base import UserFlowBlock
from telebot_constructor.user_flow.types import (
    SetupResult,
    UserFlowContext,
    UserFlowSetupContext,
)

FormFieldId = str

FormEnd: TypeAlias = None


class NextFieldMapping(BaseModel):
    cases: dict[Optional[str], Optional[FormFieldId]]
    default: FormFieldId


NextField = Union[FormEnd, FormFieldId, NextFieldMapping]


def construct_next_field_getter(next_field: NextField) -> NextFieldGetter:
    if next_field is None:
        return NextFieldGetter.form_end()
    elif isinstance(next_field, FormFieldId):
        return NextFieldGetter.by_name(next_field)
    elif isinstance(next_field, NextFieldMapping):
        next_field_mapping = next_field
        # similar to NextFieldGetter.by_mapping, but uses stringified values
        return NextFieldGetter(
            lambda _, prev_field_value: next_field_mapping.cases.get(
                prev_field_value
                if prev_field_value is None
                else str(prev_field_value),  # TODO: sync stringifying logic with admin-visible values
                next_field_mapping.default,
            ),
            possible_next_field_names=(
                [next_field_id for next_field_id in next_field_mapping.cases.values()] + [next_field_mapping.default]
            ),
        )


class BaseFormFieldConfig(BaseModel, abc.ABC):
    id: FormFieldId
    propmt: str
    is_required: bool
    result_formatting_opts: FormFieldResultFormattingOpts
    next_field: NextField

    def base_field_kwargs(self) -> dict[str, Any]:
        return dataclasses.asdict(
            FormField(
                name=self.id,
                required=self.is_required,
                query_message=self.propmt,
                next_field_getter=construct_next_field_getter(self.next_field),
                result_formatting_opts=self.result_formatting_opts,
            )
        )

    @abc.abstractmethod
    def construct_field(self) -> FormField:
        ...


class PlainTextFormFieldConfig(BaseFormFieldConfig):
    empty_text_error_msg: str

    def construct_field(self) -> PlainTextField:
        return PlainTextField(
            empty_text_error_msg=self.empty_text_error_msg,
            **self.base_field_kwargs(),
        )


class FormFieldConfig(ExactlyOneNonNullFieldModel):
    plain_text: Optional[PlainTextFormFieldConfig]

    def specific_config(self) -> BaseFormFieldConfig:
        return self.plain_text  # type: ignore


class FormMessages(BaseModel):
    form_start: str
    field_is_skippable: str
    field_is_not_skippable: str
    please_enter_correct_value: str
    unsupported_command: str
    cancelling_because_of_error: str


def _validate_template(template: str, placeholder_count: int, title: str) -> str:
    actual_placeholder_count = template.count(r"{}")
    if actual_placeholder_count != placeholder_count:
        raise ValueError(
            f'Expected {placeholder_count} "{{}}" placeholders in {title}, found {actual_placeholder_count}'
        )
    return template


class FormBlock(UserFlowBlock):
    """
    UNFINISHED

    Block with a series of questions to user with options to export their answers in various formats"""

    form_name: str
    fields: list[FormFieldConfig]
    messages: FormMessages

    form_completed_next_block_id: Optional[str]
    form_cancelled_next_block_id: Optional[str]

    async def setup(self, context: UserFlowSetupContext) -> SetupResult:
        #                                          VVV impossible to generate type anntation for
        #                                              form result type, so we use Any
        self._form_handler = ComponentsFormHandler[Any](
            redis=context.redis,
            bot_prefix=context.bot_prefix,
            name=self.form_name,
            form=ComponentsForm(
                fields=[f.specific_config().construct_field() for f in self.fields],
                allow_cyclic=False,
            ),
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
            # TODO: handle form results here:
            # + export to: specified Telegram chat, Airtable, Google Sheets, Trello
            # ? save to internal storage to show in Constructor UI
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
