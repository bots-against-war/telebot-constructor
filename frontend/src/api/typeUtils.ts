import type { UserFlowBlockConfig, UserFlowEntryPointConfig } from "./types";

export function getBlockId(c: UserFlowBlockConfig): string {
  if (c.content !== null) {
    return c.content.block_id;
  } else if (c.human_operator !== null) {
    return c.human_operator.block_id;
  } else if (c.menu !== null) {
    return c.menu.block_id;
  } else if (c.form !== null) {
    return c.form.block_id;
  } else {
    throw new Error(`getBlockId is outdated, unexpected config variant: ${c}`);
  }
}

export function getEntrypointId(c: UserFlowEntryPointConfig): string {
  if (c.command !== null) {
    return c.command.entrypoint_id;
  } else if (c.catch_all !== null) {
    return c.catch_all.entrypoint_id;
  } else if (c.regex !== null) {
    return c.regex.entrypoint_id;
  } else {
    throw new Error(`getEntrypointId is outdated, unexpected config variant: ${c}`);
  }
}
