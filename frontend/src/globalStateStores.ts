import { writable } from "svelte/store";
import type { LanguageData } from "./api/types";

export const availableLanguagesStore = writable<{ [k: string]: LanguageData }>({});
