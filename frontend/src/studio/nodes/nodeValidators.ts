import { flattenedFormFields } from "../../api/typeUtils";
import type {
  ContentBlock,
  FormBlock,
  FormBranchConfig,
  HumanOperatorBlock,
  LanguageSelectBlock,
  MenuBlock,
  SingleSelectFormFieldConfig,
} from "../../api/types";
import type { LocalizableText } from "../../types";
import { err, ok, type Result } from "../../utils";
import type { LanguageConfig } from "../stores";
import { capitalize } from "../utils";
import { formMessageName } from "./FormBlock/content";
import { getBaseFormFieldConfig } from "./FormBlock/utils";
import { PLACEHOLDER_GROUP_CHAT_ID } from "./defaultConfigs";

export interface ValidationError {
  error: string | string[];
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
        error: `${capitalize(textName)}: отсутствует локализация на язык(и): ${missingLanguages.join(", ")}`,
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
      error: results.flatMap((res) => (res.ok ? "" : res.error.error)).filter((s) => s),
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
  const results: Result<null, ValidationError>[] = [];

  if (config.feedback_handler_config.admin_chat_id === PLACEHOLDER_GROUP_CHAT_ID) {
    results.push(err({ error: "Не выбран админ-чат" }));
  }
  results.push(
    validateLocalizableText(
      config.feedback_handler_config.messages_to_user.forwarded_to_admin_ok,
      "ответ на успешно принятое сообщение",
      langConfig,
    ),
  );
  results.push(
    validateLocalizableText(
      config.feedback_handler_config.messages_to_user.throttling,
      "предупреждение, что сообщений слишком много",
      langConfig,
    ),
  );

  return mergeResults(results);
}

export function validateMenuBlock(config: MenuBlock, langConfig: LanguageConfig | null): Result<null, ValidationError> {
  const results: Result<null, ValidationError>[] = [];
  results.push(validateLocalizableText(config.menu.text, "текст сообщения с меню", langConfig));
  if (config.menu.config.back_label !== null) {
    results.push(validateLocalizableText(config.menu.config.back_label, 'текст на кнопке "назад"', langConfig));
  }

  if (config.menu.items.length === 0) {
    results.push(err({ error: "Ни одного пункта в меню" }));
  }

  for (const [idx, item] of config.menu.items.entries()) {
    results.push(validateLocalizableText(item.label, `пункт #${idx + 1}`, langConfig));
    if (!item.next_block_id) {
      results.push(err({ error: `Для пункта #${idx + 1} не выбран следующий блок` }));
    }
  }

  return mergeResults(results);
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
    results.push(err({ error: "Пустая форма" }));
  }
  results.push(
    ...flattenedFormFields(config.members).flatMap((field, idx) => {
      idx += 1; //  1-based indexing
      const resultfForField: Result<null, ValidationError>[] = [];
      const fieldBaseConfig = getBaseFormFieldConfig(field);
      resultfForField.push(
        fieldBaseConfig.name.length > 0 ? ok(null) : err({ error: `Не указано название поля #${idx}` }),
      );
      resultfForField.push(validateLocalizableText(fieldBaseConfig.prompt, `вопрос в поле #${idx}`, langConfig));
      if (field.single_select) {
        if (field.single_select.options.length === 0) {
          resultfForField.push(err({ error: `Не указано ни одного варианта выбора в поле #${idx}` }));
        }
        resultfForField.push(
          ...field.single_select.options.map(
            (eo, optionIdx) => validateLocalizableText(eo.label, `текст варианта #${optionIdx + 1} в поле #${idx}`, langConfig)
          )
        );
      }
      return mergeResults(resultfForField);
    }),
  );

  const validationResultsForBranches: Result<null, ValidationError>[] = config.members.map((member, idx) => {
    idx += 1; //  1-based indexing
    if (!member.branch) return ok(null);
    if (member.branch.members.length === 0) {
      return err({ error: `Ветвь #${idx} не включает ни одного поля` });
    }
    if (!member.branch.condition_match_value) {
      return err({ error: `Для ветви #${idx} не задано условие` });
    }
    return ok(null);
  });
  results.push(...validationResultsForBranches);

  // validating that all branches refer to valid and distinct options from a switch field
  let currentSwitchField: SingleSelectFormFieldConfig | null = null;
  let currentBranches: [FormBranchConfig, number][] = [];

  function validateCurrentBranches(): Result<null, ValidationError> {
    let branchIndices = currentBranches.map(([_, branchIdx]) => `#${branchIdx + 1}`).join(", ");
    if (currentBranches.length === 0) return ok(null);
    if (currentSwitchField === null)
      return err({ error: `Ветви (${branchIndices}) без предшествующего поля-переключателя` });
    const currentSwitchOptionIds = currentSwitchField.options.map((o) => o.id);
    const branchConditionOptionIds = currentBranches.map(([b]) => b.condition_match_value || ""); // || "" is for type safety, every branch is validated to have non-empty value
    if (branchConditionOptionIds.some((optId) => !currentSwitchOptionIds.includes(optId))) {
      return err({
        error: `Невалидная конфигурация ветвей ${branchIndices}: условие не соответвует полю-переключателю`,
      });
    }
    if (new Set(branchConditionOptionIds).size !== branchConditionOptionIds.length) {
      return err({
        error: `Ветви ${branchIndices} содержат повторяющиеся условия`,
      });
    }
    return ok(null);
  }

  for (const [idx, member] of config.members.entries()) {
    if (member.field) {
      if (currentBranches.length > 0) {
        results.push(validateCurrentBranches());
        currentBranches = [];
      }
      if (member.field.single_select) currentSwitchField = member.field.single_select;
      else currentSwitchField = null;
    } else if (member.branch) {
      currentBranches.push([member.branch, idx]);
    }
  }
  results.push(validateCurrentBranches());

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
