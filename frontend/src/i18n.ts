import { init, locale, register } from "svelte-i18n";

const LOCALSTORAGE_KEY = "locale";

const LOCALES = {
  ru: "./../locales/ru.json",
  en: "./../locales/en.json",
};

export function initI18n() {
  Object.entries(LOCALES).map(([loc, file]) => {
    register(loc, () => import(file));
  });

  init({
    fallbackLocale: "ru",
    initialLocale: localStorage.getItem(LOCALSTORAGE_KEY) || "en",
  });
}

export function setLocale(l: string) {
  locale.set(l);
  localStorage.setItem(LOCALSTORAGE_KEY, l);
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
