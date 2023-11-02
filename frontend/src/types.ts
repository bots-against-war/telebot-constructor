import { type BotConfig, type BotInfo } from "./api/types";

// see svelvet's docs
export type SvelvetConnection = string | number | [string | number, string | number];

export interface SvelvetPosition {
  x: number;
  y: number;
}

export interface BotConfigList {
  [key: string]: BotConfig;
}

export interface BotInfoList {
  [key: string]: BotInfo;
}

export type MultilangText = { [k: string]: string };

export type LocalizableText = string | MultilangText;
