import { type FormMessages } from "../../../api/types";
import { type MessageFormatter } from "../../../i18n";
import type { FormErrorMessages } from "./prefill";

interface FormExampleContent {
  name: string;
  prompt: string;
}

export const EXAMPLE_CONTENT: FormExampleContent[] = [
  {
    name: "studio.form.placeholders.01_name",
    prompt: "studio.form.placeholders.01_prompt",
  },
  {
    name: "studio.form.placeholders.02_name",
    prompt: "studio.form.placeholders.02_prompt",
  },
  {
    name: "studio.form.placeholders.03_name",
    prompt: "studio.form.placeholders.03_prompt",
  },
  {
    name: "studio.form.placeholders.04_name",
    prompt: "studio.form.placeholders.04_prompt",
  },
  {
    name: "studio.form.placeholders.05_name",
    prompt: "studio.form.placeholders.05_prompt",
  },
  {
    name: "studio.form.placeholders.06_name",
    prompt: "studio.form.placeholders.06_prompt",
  },
  {
    name: "studio.form.placeholders.07_name",
    prompt: "studio.form.placeholders.07_prompt",
  },
  {
    name: "studio.form.placeholders.08_name",
    prompt: "studio.form.placeholders.08_prompt",
  },
  {
    name: "studio.form.placeholders.09_name",
    prompt: "studio.form.placeholders.09_prompt",
  },
  {
    name: "studio.form.placeholders.10_name",
    prompt: "studio.form.placeholders.10_prompt",
  },
  {
    name: "studio.form.placeholders.11_name",
    prompt: "studio.form.placeholders.11_prompt",
  },
  {
    name: "studio.form.placeholders.12_name",
    prompt: "studio.form.placeholders.12_prompt",
  },
  {
    name: "studio.form.placeholders.13_name",
    prompt: "studio.form.placeholders.13_prompt",
  },
  {
    name: "studio.form.placeholders.14_name",
    prompt: "studio.form.placeholders.14_prompt",
  },
  {
    name: "studio.form.placeholders.15_name",
    prompt: "studio.form.placeholders.15_prompt",
  },
  {
    name: "studio.form.placeholders.16_name",
    prompt: "studio.form.placeholders.16_prompt",
  },
  {
    name: "studio.form.placeholders.17_name",
    prompt: "studio.form.placeholders.17_prompt",
  },
  {
    name: "studio.form.placeholders.18_name",
    prompt: "studio.form.placeholders.18_prompt",
  },
];

export function getRandomContent(t: MessageFormatter): FormExampleContent {
  const idx = Math.floor(Math.random() * EXAMPLE_CONTENT.length);
  const keys = EXAMPLE_CONTENT[idx];
  return {
    name: t(keys.name),
    prompt: t(keys.prompt),
  };
}

const EXAMPLE_START_MESSAGE_KEYS: string[] = [
  "studio.form.placeholders.start_1",
  "studio.form.placeholders.start_2",
  "studio.form.placeholders.start_3",
  "studio.form.placeholders.start_4",
];

export function getRandomFormStartMessage(t: MessageFormatter): string {
  const idx = Math.floor(Math.random() * EXAMPLE_START_MESSAGE_KEYS.length);
  return t(EXAMPLE_START_MESSAGE_KEYS[idx]);
}

export function formMessageName(
  key: keyof FormMessages | keyof FormErrorMessages | string,
  t: MessageFormatter,
): string {
  switch (key) {
    case "form_start":
      return t("studio.form.messages.form_start");
    case "cancel_command_is":
      return t("studio.form.messages.cancel_cmd");
    case "field_is_skippable":
      return t("studio.form.messages.field_is_skippable");
    case "field_is_not_skippable":
      return t("studio.form.messages.field_isnt_skippable");
    case "please_enter_correct_value":
      return t("studio.form.messages.enter_correct_value");
    case "unsupported_command":
      return t("studio.form.messages.unsupported_cmd");
    case "empty_text_error_msg":
      return t("studio.form.messages.empty_text_error");
    case "not_an_integer_error_msg":
      return t("studio.form.messages.invalid_number_error");
    case "not_an_integer_list_error_msg":
      return t("studio.form.messages.invalid_number_list_error");
    case "bad_time_format_msg":
      return t("studio.form.messages.invalid_date_error");
    case "invalid_enum_error_msg":
      return t("studio.form.messages.invalid_enum_error");
    case "attachments_expected_error_msg":
      return t("studio.form.messages.no_attachment_error");
    case "only_one_media_message_allowed_error_msg":
      return t("studio.form.messages.too_many_attachments_error");
    case "bad_attachment_type_error_msg":
      return t("studio.form.messages.unsupported_attachment_error");
    case "please_use_inline_menu":
      return t("studio.form.messages.use_inline_menu_error");
    default:
      return key;
  }
}

export function formMessageDescription(
  key: keyof FormMessages | keyof FormErrorMessages | string,
  t: MessageFormatter,
): string | null {
  switch (key) {
    case "field_is_not_skippable":
      return t("studio.form.messages.field_isnt_skippable_descr");
    default:
      return null;
  }
}
