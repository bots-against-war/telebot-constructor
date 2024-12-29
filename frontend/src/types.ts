// see svelvet's docs
export type SvelvetConnection = string | number | [string | number, string | number];

export interface SvelvetPosition {
  x: number;
  y: number;
}

export type MultilangText = { [k: string]: string };

export type LocalizableText = string | MultilangText;
