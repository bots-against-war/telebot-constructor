import type { BaseFormFieldConfig, FormFieldConfig } from "../../../api/types";

export function getBaseFormFieldConfig(config: FormFieldConfig): BaseFormFieldConfig {
  if (config.plain_text) {
    return config.plain_text;
  } else if (config.single_select) {
    return config.single_select;
  } else {
    throw new Error("Unexpected config variant, getBaseFormFieldConfig is probably outdated");
  }
}

export function getFormFieldId(config: FormFieldConfig): string {
  return getBaseFormFieldConfig(config).id;
}

export function getDefaultBaseFormFieldConfig(): BaseFormFieldConfig {
  return {
    id: `form_field_${crypto.randomUUID()}`,
    name: "",
    prompt: "",
    is_required: true,
    result_formatting: "auto",
  };
}

export function getDefaultFormFieldConfig(
  baseConfig: BaseFormFieldConfig,
  key: keyof FormFieldConfig,
): FormFieldConfig {
  switch (key) {
    case "plain_text": {
      return {
        plain_text: {
          ...baseConfig,
          is_long_text: false,
          empty_text_error_msg: "",
        },
      };
    }
    case "single_select": {
      return {
        single_select: {
          ...baseConfig,
          options: [],
          invalid_enum_error_msg: "",
        },
      };
    }
  }
  throw new Error(`getDefaultFormFieldConfig can't create config with key ${key}`);
}
