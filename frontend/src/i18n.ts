import { init, locale, register } from "svelte-i18n";

const LOCALSTORAGE_KEY = "locale";

export function initI18n() {
  register("ru", () => import("./../locales/ru.json"));
  register("en", () => import("./../locales/en.json"));
  init({
    fallbackLocale: "ru",
    initialLocale: localStorage.getItem(LOCALSTORAGE_KEY) || "en",
  });
}

export function setLocale(l: string) {
  locale.set(l);
  localStorage.setItem(LOCALSTORAGE_KEY, l);
}
