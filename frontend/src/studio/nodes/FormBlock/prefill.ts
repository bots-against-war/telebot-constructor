import { type FormMessages } from "../../../api/types";
import type { I18NLocale, MessageFormatter } from "../../../i18n";
import type { LocalizableText } from "../../../types";
import type { LanguageConfig } from "../../stores";
import { clone } from "../../utils";
import { validateLocalizableText } from "../nodeValidators";

export type PrefillableFormErrorKey =
  | "empty_text_error_msg"
  | "not_an_integer_error_msg"
  | "not_an_integer_list_error_msg"
  | "bad_time_format_msg"
  | "invalid_enum_error_msg"
  | "attachments_expected_error_msg"
  | "only_one_media_message_allowed_error_msg"
  | "bad_attachment_type_error_msg"
  | "please_use_inline_menu";

export const PREFILLABLE_FORM_ERROR_KEYS: PrefillableFormErrorKey[] = [
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

export type FormErrorMessages = Partial<Record<PrefillableFormErrorKey, LocalizableText>>;

type PrefillableFormMessageKey = Exclude<keyof FormMessages, "form_start">;
export const PREFILLABLE_FORM_MESSAGE_KEYS: PrefillableFormMessageKey[] = [
  "field_is_skippable",
  "field_is_not_skippable",
  "cancel_command_is",
  "please_enter_correct_value",
  "unsupported_command",
];

type PrefillableKey = PrefillableFormMessageKey | PrefillableFormErrorKey;
const PREFILLABLE_KEYS: PrefillableKey[] = [...PREFILLABLE_FORM_MESSAGE_KEYS, ...PREFILLABLE_FORM_ERROR_KEYS];

export type PrefilledMessages = Partial<Record<PrefillableKey, { [k: string]: string }>>;

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

export function prefilledMessage(
  prefilledMessages: PrefilledMessages,
  key: PrefillableKey,
  langConfig: LanguageConfig | null,
  locale: I18NLocale,
): LocalizableText {
  const messages = prefilledMessages[key] || {};
  if (langConfig === null) {
    return (locale && locale in messages ? messages[locale] : messages["en"]) || "";
  } else {
    return Object.fromEntries(
      langConfig.supportedLanguageCodes.map((supportedLang) => [supportedLang, messages[supportedLang] || ""]),
    );
  }
}

// T must be a string -> LocalizableText object, but I can't figure out how to express it correctly in TS... :(
export function updateWithPrefilled<T>(
  messages: T,
  langConfig: LanguageConfig | null,
  t: MessageFormatter,
  locale: I18NLocale,
): [T, string[]] {
  // console.debug(`Prefilling ${JSON.stringify(messages)}`);
  const prefilledMessages = getPrefilledMessages();
  const messagesCopy = clone(messages);
  const prefilledKeys: string[] = [];
  for (const key of PREFILLABLE_KEYS) {
    // @ts-expect-error
    if (key in messagesCopy && !validateLocalizableText(messagesCopy[key], "", langConfig, t).ok) {
      const pm = prefilledMessage(prefilledMessages, key, langConfig, locale);
      // @ts-expect-error
      messagesCopy[key] = pm;
      prefilledKeys.push(key);
    }
  }
  // console.debug(`Prefilling result: ${JSON.stringify(messagesCopy)}, keys ${prefilledKeys}`);
  return [messagesCopy, prefilledKeys];
}
