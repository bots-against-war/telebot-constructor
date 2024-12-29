import { writable } from "svelte/store";
import { type LanguageData, type LoggedInUser } from "./api/types";
import { err, ok, type Result } from "./utils";

export const availableLanguagesStore = writable<{ [k: string]: LanguageData }>({});

export function lookupLanguage(
  language: string,
  availableLanguages: { [k: string]: LanguageData },
): Result<LanguageData> {
  if (!(language in availableLanguages)) {
    return err(`unknown language code ${language}`);
  } else {
    return ok(availableLanguages[language]);
  }
}

export const loggedInUserStore = writable<LoggedInUser>();
