import { SvelteComponent } from "svelte";
import type { Newable } from "ts-essentials";
import {
  CodeSolid,
  GlobeSolid,
  UserHeadsetSolid,
  CodeForkSolid,
  NewspaperSolid,
  ClipboardSolid,
  InfoCircleSolid,
} from "flowbite-svelte-icons";

export enum NodeTypeKey {
  command = "command",
  content = "content",
  human_operator = "human_operator",
  language_select = "language_select",
  menu = "menu",
  form = "form",
  info = "info",
}

export const NODE_HUE: { [key in NodeTypeKey]: number } = {
  command: 280,
  content: 25,
  human_operator: 345,
  language_select: 220,
  menu: 120,
  form: 67,
  info: 0, // white is used
};

export function headerColor(hue: number): string {
  return `hsl(${hue}, 70%, 70%)`;
}

export const NODE_TITLE: { [key in NodeTypeKey]: string } = {
  command: "Команда",
  content: "Контент",
  human_operator: "Оператор:ка",
  language_select: "Язык",
  menu: "Меню",
  form: "Форма",
  info: "Аккаунт бота",
};

export const NODE_ICON: { [key in NodeTypeKey]: Newable<SvelteComponent> } = {
  command: CodeSolid,
  content: NewspaperSolid,
  human_operator: UserHeadsetSolid,
  language_select: GlobeSolid,
  menu: CodeForkSolid,
  form: ClipboardSolid,
  info: InfoCircleSolid,
};
