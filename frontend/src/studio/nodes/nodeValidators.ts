import type { ContentBlock, FormBlock, HumanOperatorBlock, LanguageSelectBlock } from "../../api/types";
import type { LocalizableText } from "../../types";
import { err, ok, type Result } from "../../utils";
import type { LanguageConfig } from "../stores";
import { PLACEHOLDER_GROUP_CHAT_ID } from "./defaultConfigs";

export interface ValidationError {
  error: string;
}

function validateLocalizableText(
  text: LocalizableText,
  textName: string,
  langConfig: LanguageConfig | null,
): Result<null, ValidationError> {
  if (langConfig === null) {
    if (typeof text === "object") {
      return err({
        error: `${textName}: Задана локализация (${Object.keys(text).join(", ")}), но в боте нет выбора языков`,
      });
    } else if (text.length === 0) {
      return err({ error: `${textName}: не заполнен` });
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
      return err({ error: `${textName}: отсутствует локализация на языки: ${missingLanguages.join(", ")}` });
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
      return validateLocalizableText(content.text.text, `Текст #${idx + 1}`, langConfig);
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
    return validateLocalizableText(config.menu_config.propmt, "Текст в сообщении-меню", langConfig);
  }
}

export function validateFormBlock(config: FormBlock, langConfig: LanguageConfig | null): Result<null, ValidationError> {
  if (config.members.length === 0) {
    return err({ error: "В форму не добавлено ни одного поля" });
  }
  const messagesValidationResult = mergeResults(
    Object.entries(config.messages).map(([key, text]) =>
      validateLocalizableText(
        // @ts-expect-error
        text,
        key,
        langConfig,
      ),
    ),
  );
  if (!messagesValidationResult.ok) return messagesValidationResult;

  if (!(config.results_export.echo_to_user || config.results_export.to_chat)) {
    return err({ error: "Не выбрана обработка результатов формы" });
  }
  return ok(null);
}
