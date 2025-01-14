import { addMessages, init, locale } from "svelte-i18n";
import en from "../locales/en.json";
import ru from "../locales/ru.json";

const LOCALSTORAGE_KEY = "locale";

export function initI18n() {
  addMessages("ru", ru);
  addMessages("en", en);
  // NOTE: when adding more locales, consider async loading with register
  // this will require copying locales to "public" dir and setting up
  // static file serving on backend)

  init({
    fallbackLocale: "en",
    initialLocale: localStorage.getItem(LOCALSTORAGE_KEY) || "en",
  });
}

export function setLocale(loc: string) {
  locale.set(loc);
  localStorage.setItem(LOCALSTORAGE_KEY, loc);
}

// the types are not exported from i18n, so we copy them here
type InterpolationValues = Record<string, string | number | boolean | Date | null | undefined> | undefined;
export interface MessageObject {
  id: string;
  locale?: string;
  format?: string;
  default?: string;
  values?: InterpolationValues;
}
export type MessageFormatter = (id: string | MessageObject, options?: Omit<MessageObject, "id">) => string;

export type I18NLocale = string | null | undefined;
