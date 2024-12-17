import {
  flattenedFormBranches,
  flattenedFormFields,
  getBlockId,
  getEntrypointConcreteConfig,
  getEntrypointId,
} from "../api/typeUtils";
import type { NodeDisplayCoords, UserFlowBlockConfig, UserFlowConfig, UserFlowEntryPointConfig } from "../api/types";
import { BOT_INFO_NODE_ID } from "../constants";
import type { LocalizableText } from "../types";
import { generateFormFieldId, generateOptionId, getBaseFormFieldConfig } from "./nodes/FormBlock/utils";
import { generateFormName } from "./nodes/defaultConfigs";
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

// for display purposes and some internal pre-filling
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
    // form names must be unique within one bot
    config.form.form_name = generateFormName();

    // re-generating form fields' ids and option ids
    // opt ids must be regenerated consistently between options and branches
    const optIdMapping: Record<string, string> = {};
    flattenedFormFields(config.form.members).forEach((field) => {
      getBaseFormFieldConfig(field).id = generateFormFieldId();
      if (field.single_select) {
        field.single_select.options.forEach((opt) => {
          const newOptId = generateOptionId();
          optIdMapping[opt.id] = generateOptionId();
          opt.id = newOptId;
        });
      }
    });
    flattenedFormBranches(config.form.members).forEach((branch) => {
      const oldOptId = branch.condition_match_value;
      if (oldOptId) {
        const newOptId = optIdMapping[oldOptId];
        branch.condition_match_value = newOptId;
      }
    });
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

export function filterNodeDisplayCoords(coords: NodeDisplayCoords, config: UserFlowConfig): NodeDisplayCoords {
  return Object.fromEntries(
    Object.entries(coords).filter(
      ([id, _]) =>
        id === BOT_INFO_NODE_ID ||
        config.entrypoints.some((ep) => getEntrypointId(ep) == id) ||
        config.blocks.some((block) => getBlockId(block) == id),
    ),
  );
}

export interface BoundingBox {
  xMin: number;
  xMax: number;
  yMin: number;
  yMax: number;
}

export function boundingBox(coords: NodeDisplayCoords, width: number, height: number): BoundingBox {
  if (Object.entries(coords).length == 0) {
    return {
      xMax: 0,
      xMin: 0,
      yMax: 0,
      yMin: 0,
    };
  }
  const xCoords = Object.values(coords).map(({ x }) => x);
  const yCoords = Object.values(coords).map(({ y }) => y);
  return {
    xMax: Math.max.apply(null, xCoords) + width / 2,
    xMin: Math.min.apply(null, xCoords) - width / 2,
    yMax: Math.max.apply(null, yCoords) + height / 2,
    yMin: Math.min.apply(null, yCoords) - height / 2,
  };
}
