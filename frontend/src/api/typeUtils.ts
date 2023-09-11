import type { UserFlowBlockConfig, UserFlowEntryPointConfig } from "./types";

export function getBlockId(c: UserFlowBlockConfig): string {
  if (c.message !== null) {
    return c.message.block_id;
  } else if (c.human_operator !== null) {
    return c.human_operator.block_id;
  } else {
    throw new Error(`getBlockId is outdated, unexpected config variant: ${c}`);
  }
}

export function getEntrypointId(c: UserFlowEntryPointConfig): string {
  if (c.command !== null) {
    return c.command.entrypoint_id;
  } else {
    throw new Error(`getEntrypointId is outdated, unexpected config variant: ${c}`);
  }
}
