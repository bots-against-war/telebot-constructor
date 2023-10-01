import { type BotConfig } from "./api/types";

// see svelvet's docs
export type SvelvetConnection = string | number | [string | number, string | number];

export interface SvelvetPosition {
  x: number;
  y: number;
}

export interface BotConfigList {
  [key: string]: BotConfig;
}
