import { writable } from "svelte/store";
import { type SupportedLanguages } from "../api/types";

export interface LanguageConfig {
  supportedLanguageCodes: SupportedLanguages;
  defaultLanguageCode: string;
}

export const languageConfigStore = writable<LanguageConfig | null>(null);
