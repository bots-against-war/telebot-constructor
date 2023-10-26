import { type FormMessages } from "../../../api/types";
import type { LocalizableText } from "../../../types";
import type { LanguageConfig } from "../../stores";
import { validateLocalizableText } from "../nodeValidators";

type PrefilledErrorMessageKey =
  | "empty_text_error_msg"
  | "not_an_integer_error_msg"
  | "not_an_integer_list_error_msg"
  | "bad_time_format_msg"
  | "invalid_enum_error_msg"
  | "attachments_expected_error_msg"
  | "only_one_media_message_allowed_error_msg"
  | "bad_attachment_type_error_msg"
  | "please_use_inline_menu";

type PrefilledKey = Exclude<keyof FormMessages, "form_start"> | PrefilledErrorMessageKey;
const PREFILLABLE_KEYS: PrefilledKey[] = [
  "field_is_skippable",
  "field_is_not_skippable",
  "field_is_not_skippable",
  "please_enter_correct_value",
  "unsupported_command",
  "empty_text_error_msg",
  "not_an_integer_error_msg",
  "not_an_integer_list_error_msg",
  "bad_time_format_msg",
  "invalid_enum_error_msg",
  "attachments_expected_error_msg",
  "only_one_media_message_allowed_error_msg",
  "bad_attachment_type_error_msg",
  "please_use_inline_menu",
];

export type PrefilledMessages = Partial<Record<PrefilledKey, { [k: string]: string }>>;

const PREFILLED_FORM_MESSAGES_KEY = "prefilledFormMessages";

export function getPrefilledMessages(): PrefilledMessages {
  const dump = localStorage.getItem(PREFILLED_FORM_MESSAGES_KEY);
  if (!dump) {
    return {};
  }
  return JSON.parse(dump);
}

export function savePrefilledMessages(update: PrefilledMessages) {
  const existing = getPrefilledMessages();
  const merged: PrefilledMessages = {};
  for (const key of PREFILLABLE_KEYS) {
    merged[key] = { ...(existing[key] || {}), ...(update[key] || {}) };
  }
  localStorage.setItem(PREFILLED_FORM_MESSAGES_KEY, JSON.stringify(merged));
}

// constructor's interface lang, NOT the default bot langauge from LanguageConfig
const DEFAULT_LANGUAGE = "ru";

export function prefilledMessage(
  prefilledMessages: PrefilledMessages,
  key: PrefilledKey,
  langConfig: LanguageConfig | null,
): LocalizableText {
  if (langConfig === null) {
    return (prefilledMessages[key] || {})[DEFAULT_LANGUAGE] || "";
  } else {
    return Object.fromEntries(
      langConfig.supportedLanguageCodes.map((supportedLang) => [
        supportedLang,
        (prefilledMessages[key] || {})[supportedLang] || "",
      ]),
    );
  }
}

export function updateWithPrefilled(messages: FormMessages, langConfig: LanguageConfig | null): FormMessages {
  const prefilledMessages = getPrefilledMessages();
  const messagesCopy = JSON.parse(JSON.stringify(messages));
  for (const key of PREFILLABLE_KEYS) {
    if (key in messagesCopy && !validateLocalizableText(messagesCopy[key], "", langConfig).ok) {
      messagesCopy[key] = prefilledMessage(prefilledMessages, key, langConfig);
    }
  }
  return messagesCopy;
}
