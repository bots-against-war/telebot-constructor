import type { FormFieldConfig } from "../../../api/types";

export function getFormFieldId(config: FormFieldConfig): string {
  if (config.plain_text) {
    return config.plain_text.id;
  } else if (config.single_select) {
    return config.single_select.id;
  } else {
    throw new Error("Unexpected config variant, getFormFieldId is probably outdated");
  }
}
