import type { UserFlowBlockConfig, UserFlowEntryPointConfig } from "./types";

export function getBlockId(c: UserFlowBlockConfig): string {
  if (c.content) {
    return c.content.block_id;
  } else if (c.human_operator) {
    return c.human_operator.block_id;
  } else if (c.menu) {
    return c.menu.block_id;
  } else if (c.form) {
    return c.form.block_id;
  } else if (c.language_select) {
    return c.language_select.block_id;
  } else {
    throw new Error(`getBlockId got unexpected config variant: ${c}`);
  }
}

export function getEntrypointId(c: UserFlowEntryPointConfig): string {
  if (c.command) {
    return c.command.entrypoint_id;
  } else if (c.catch_all) {
    return c.catch_all.entrypoint_id;
  } else if (c.regex) {
    return c.regex.entrypoint_id;
  } else {
    throw new Error(`getEntrypointId got unexpected config variant: ${c}`);
  }
}
