import { flattenedFormFields } from "../../api/typeUtils";
import type { ContentBlock, FormBlock, HumanOperatorBlock, LanguageSelectBlock } from "../../api/types";
import type { LocalizableText } from "../../types";
import { err, ok, type Result } from "../../utils";
import type { LanguageConfig } from "../stores";
import { capitalize } from "../utils";
import { formMessageName } from "./FormBlock/content";
import { getBaseFormFieldConfig } from "./FormBlock/utils";
import { PLACEHOLDER_GROUP_CHAT_ID } from "./defaultConfigs";

export interface ValidationError {
  error: string;
}

export function validateLocalizableText(
  text: LocalizableText,
  textName: string,
  langConfig: LanguageConfig | null,
): Result<null, ValidationError> {
  if (langConfig === null) {
    if (typeof text === "object") {
      return err({
        error: `${capitalize(textName)}: задана локализация (${Object.keys(text).join(
          ", ",
        )}), но в боте нет выбора языков`,
      });
    } else if (text.length === 0) {
      return err({ error: `Не заполнен ${textName}` });
    }
  } else if (langConfig !== null) {
    let missingLanguages: string[];
    if (typeof text === "string") {
      missingLanguages = langConfig.supportedLanguageCodes;
    } else {
      missingLanguages = langConfig.supportedLanguageCodes.filter(
        (lang) => !text[lang], // filtering out missing and empty localizations
      );
    }
    if (missingLanguages.length > 0) {
      return err({
        error: `${capitalize(textName)}: отсутствует локализация на языки: ${missingLanguages.join(", ")}`,
      });
    } else {
      return ok(null);
    }
  }
  return ok(null);
}

function mergeResults(results: Result<null, ValidationError>[]): Result<null, ValidationError> {
  if (results.some((res) => !res.ok)) {
    return err({
      error: results
        .map((res) => (res.ok ? "" : res.error.error))
        .filter((s) => s)
        .join("; "),
    });
  } else {
    return ok(null);
  }
}

export function validateContentBlock(
  config: ContentBlock,
  langConfig: LanguageConfig | null,
): Result<null, ValidationError> {
  const textValidationResults: Result<null, ValidationError>[] = config.contents.map((content, idx) => {
    if (content.text) {
      return validateLocalizableText(content.text.text, `текст #${idx + 1}`, langConfig);
    } else {
      // TODO: attachments validation
      return ok(null);
    }
  });
  return mergeResults(textValidationResults);
}

export function validateHumanOperatorBlock(
  config: HumanOperatorBlock,
  langConfig: LanguageConfig | null,
): Result<null, ValidationError> {
  if (config.feedback_handler_config.admin_chat_id === PLACEHOLDER_GROUP_CHAT_ID) {
    return err({ error: "Не выбран админ-чат" });
  } else {
    return ok(null);
  }
}

export function validateLanguageSelectBlock(
  config: LanguageSelectBlock,
  langConfig: LanguageConfig | null,
): Result<null, ValidationError> {
  if (config.supported_languages.length === 0) {
    return err({ error: "Не выбраны поддерживаемые языки" });
  } else if (!config.default_language) {
    return err({ error: "Не выбран язык по умолчанию" });
  } else if (!config.supported_languages.includes(config.default_language)) {
    return err({ error: "Язык по умолчанию не входит в список поддерживаемых языков" });
  } else {
    return validateLocalizableText(config.menu_config.propmt, "текст в сообщении-меню", langConfig);
  }
}

export function validateFormBlock(config: FormBlock, langConfig: LanguageConfig | null): Result<null, ValidationError> {
  const results: Result<null, ValidationError>[] = [];
  if (config.members.length === 0) {
    results.push(err({ error: "В форму не добавлено ни одного поля" }));
  }
  results.push(
    ...flattenedFormFields(config.members).flatMap((field, idx) => {
      const fieldBaseConfig = getBaseFormFieldConfig(field);
      const results: Result<null, ValidationError>[] = [];
      results.push(fieldBaseConfig.name.length > 0 ? ok(null) : err({ error: `Не указано название поля #${idx}` }));
      results.push(validateLocalizableText(fieldBaseConfig.prompt, `вопрос в поле #${idx}`, langConfig));
      if (field.single_select && field.single_select.options.length === 0) {
        results.push(err({ error: `Не указано ни одного варианта выбора в поле #${idx}` }));
      }
      return mergeResults(results);
    }),
  );
  results.push(
    ...Object.entries(config.messages).map(([key, text]) =>
      validateLocalizableText(text, `текст сообщения "${formMessageName(key)}"`, langConfig),
    ),
  );
  if (!(config.results_export.echo_to_user || config.results_export.to_chat)) {
    results.push(err({ error: "Не выбран ни один вариант обработки результатов формы" }));
  }
  if (config.results_export.to_chat !== null && config.results_export.to_chat.chat_id === PLACEHOLDER_GROUP_CHAT_ID) {
    results.push(err({ error: "Не выбран чат для экспорта результатов" }));
  }
  return mergeResults(results);
}
