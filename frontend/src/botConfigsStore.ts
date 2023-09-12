import { writable } from "svelte/store";
import type { Writable } from "svelte/store";
import type { BotConfig } from "./api/types";

export const botConfigs: Writable<{ [key: string]: BotConfig }> = writable({});
