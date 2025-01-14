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

export type PrefillableKey = PrefillableFormMessageKey | PrefillableFormErrorKey | "anti_spam_warning";
const PREFILLABLE_KEYS: PrefillableKey[] = [
  ...PREFILLABLE_FORM_MESSAGE_KEYS,
  ...PREFILLABLE_FORM_ERROR_KEYS,
  "anti_spam_warning",
];

export type PrefilledMessages = Partial<Record<PrefillableKey, { [k: string]: string }>>;

const PREFILLED_FORM_MESSAGES_KEY = "prefilledFormMessages";

export function loadPrefilledMessages(): PrefilledMessages {
  const dump = localStorage.getItem(PREFILLED_FORM_MESSAGES_KEY);
  if (!dump) {
    return {};
  }
  return JSON.parse(dump);
}

export function savePrefilledMessages(update: PrefilledMessages) {
  const existing = loadPrefilledMessages();
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
    // no languages in the bot's config = try to fallback to interface language
    return (locale ? messages[locale] : null) || messages["en"] || "";
  } else {
    return Object.fromEntries(
      langConfig.supportedLanguageCodes.map((supportedLang) => [supportedLang, messages[supportedLang] || ""]),
    );
  }
}

export function applyPrefilledMessage(
  pm: PrefilledMessages,
  key: PrefillableKey,
  langConfig: LanguageConfig | null,
  t: MessageFormatter,
  locale: I18NLocale,
  existing: LocalizableText,
): LocalizableText {
  if (validateLocalizableText(existing, "", langConfig, t).ok) return existing;

  const prefill = prefilledMessage(pm, key, langConfig, locale);
  if (typeof prefill == "string") {
    return prefill;
  } else {
    return { ...prefill, ...(existing instanceof Object ? existing : {}) };
  }
}

// T must be a string -> LocalizableText object, but I can't figure out how to express it correctly in TS... :(
export function updatedWithPrefilled<T>(
  messages: T,
  langConfig: LanguageConfig | null,
  t: MessageFormatter,
  locale: I18NLocale,
): T {
  console.debug(`Prefilling...`, messages);
  const pm = loadPrefilledMessages();
  const messagesOut = clone(messages) as { [k: string]: LocalizableText };
  for (const key of PREFILLABLE_KEYS) {
    if (key in messagesOut) {
      messagesOut[key] = applyPrefilledMessage(pm, key, langConfig, t, locale, messagesOut[key]);
    }
  }
  console.debug(`Updated with prefilled messages`, messagesOut);
  return messagesOut as T;
}
