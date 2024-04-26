import { getBlockId, getEntrypointConcreteConfig, getEntrypointId } from "../api/typeUtils";
import type { BotConfig, NodeDisplayCoords, UserFlowBlockConfig, UserFlowEntryPointConfig } from "../api/types";
import { BOT_INFO_NODE_ID } from "../constants";
import type { LocalizableText } from "../types";
import { NodeTypeKey, getNodeTypeKey } from "./nodes/display";
import type { LanguageConfig } from "./stores";

export enum NodeKind {
  block = "block",
  entrypoint = "entrypoin",
}

export interface TentativeNode {
  kind: NodeKind;
  typeKey: NodeTypeKey;
  id: string;
  config: UserFlowEntryPointConfig | UserFlowEntryPointConfig;
}

export function generateNodeId(kind: NodeKind, type: NodeTypeKey) {
  return `${kind}-${type}-${crypto.randomUUID()}`;
}

export function svelvetNodeIdToBlockId(id: string): string {
  // svelvet adds "N-" prefix to ids we pass to them, so we need to strip id back
  // see https://svelvet.mintlify.app/components/node#props
  return id.replace(/^N-/, "");
}

export function range(size: number, start: number, step: number): number[] {
  return [...Array(size).keys()].map((i) => start + step * i);
}

export function base64Image(b64: string): string {
  return `data:image/png;base64,${b64}`;
}

export function capitalize(string: string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

// for display purposes only
export function localizableTextToString(lc: LocalizableText, langConfig: LanguageConfig | null): string {
  if (langConfig === null && typeof lc === "string") return lc;
  else if (langConfig !== null && typeof lc === "object") return lc[langConfig.defaultLanguageCode] || "";
  else return "";
}

export function clone<T>(jsonSerializable: T): T {
  return JSON.parse(JSON.stringify(jsonSerializable));
}

export function cloneEntrypointConfig(c: UserFlowEntryPointConfig): TentativeNode {
  const config = clone(c);
  const concrete = getEntrypointConcreteConfig(config);
  if (!concrete) {
    throw "Failed to get concrete entrypoint config from config";
  }
  const typeKey = getNodeTypeKey(config);
  if (!typeKey) {
    throw "Failed to get node type key from config";
  }
  const id = generateNodeId(NodeKind.entrypoint, typeKey);
  concrete.entrypoint_id = id;
  concrete.next_block_id = null;
  return {
    kind: NodeKind.entrypoint,
    typeKey,
    id,
    config,
  };
}

export function cloneBlockConfig(c: UserFlowBlockConfig): TentativeNode {
  const config = clone(c);
  const typeKey = getNodeTypeKey(config);
  if (!typeKey) {
    throw "Failed to get node type key from config";
  }
  const id = generateNodeId(NodeKind.block, typeKey);
  if (config.content) {
    config.content.block_id = id;
    config.content.next_block_id = null;
  } else if (config.form) {
    config.form.block_id = id;
    config.form.form_cancelled_next_block_id = null;
    config.form.form_completed_next_block_id = null;
  } else if (config.human_operator) {
    config.human_operator.block_id = id;
  } else if (config.language_select) {
    config.language_select.block_id = id;
    config.language_select.next_block_id = null;
    config.language_select.language_selected_next_block_id = null;
  } else if (config.menu) {
    config.menu.block_id = id;
    for (const menuItem of config.menu.menu.items) {
      menuItem.next_block_id = null;
    }
  }
  return {
    kind: NodeKind.block,
    typeKey,
    id,
    config,
  };
}

export function filterNodeDisplayCoords(coords: NodeDisplayCoords, config: BotConfig): NodeDisplayCoords {
  return Object.fromEntries(
    Object.entries(coords).filter(
      ([id, _]) =>
        id === BOT_INFO_NODE_ID ||
        config.user_flow_config.entrypoints.some((ep) => getEntrypointId(ep) == id) ||
        config.user_flow_config.blocks.some((block) => getBlockId(block) == id),
    ),
  );
}
