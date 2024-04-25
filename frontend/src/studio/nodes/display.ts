import {
  ClipboardSolid,
  CodeForkSolid,
  CodeSolid,
  GlobeSolid,
  InfoCircleSolid,
  NewspaperSolid,
  UserHeadsetSolid,
} from "flowbite-svelte-icons";
import { SvelteComponent } from "svelte";
import type { Newable } from "ts-essentials";
import type { UserFlowBlockConfig, UserFlowEntryPointConfig } from "../../api/types";

export enum NodeTypeKey {
  command = "command",
  content = "content",
  human_operator = "human_operator",
  language_select = "language_select",
  menu = "menu",
  form = "form",
  info = "info",
}

export function getNodeTypeKey(config: UserFlowBlockConfig | UserFlowEntryPointConfig): NodeTypeKey | null {
  if (config.command) {
    return NodeTypeKey.command;
  } else if (config.content) {
    return NodeTypeKey.content;
  } else if (config.human_operator) {
    return NodeTypeKey.human_operator;
  } else if (config.language_select) {
    return NodeTypeKey.language_select;
  } else if (config.menu) {
    return NodeTypeKey.menu;
  } else if (config.form) {
    return NodeTypeKey.form;
  } else {
    return null;
  }
}

export const NODE_HUE: { [key in NodeTypeKey]: number } = {
  command: 280,
  content: 25,
  human_operator: 345,
  language_select: 220,
  menu: 120,
  form: 67,
  info: 0, // = white
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
