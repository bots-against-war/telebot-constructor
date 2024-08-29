import type {
  BotDeletedEvent,
  BotEditedEvent,
  BotStartedEvent,
  BotStoppedEvent,
  BranchingFormMemberConfig,
  FormBranchConfig,
  FormFieldConfig,
  UserFlowBlockConfig,
  UserFlowEntryPointConfig,
} from "./types";

export type AnyBotEvent = BotStoppedEvent | BotDeletedEvent | BotStartedEvent | BotEditedEvent;

export function botEventTimestamp(e: AnyBotEvent): number {
  return e.timestamp || 0;
}

export function getBlockConcreteConfig(c: UserFlowBlockConfig) {
  return c.content || c.human_operator || c.menu || c.form || c.language_select;
}

export function getBlockId(c: UserFlowBlockConfig): string {
  const concreteConfig = getBlockConcreteConfig(c);
  if (concreteConfig) {
    return concreteConfig.block_id;
  } else {
    throw new Error(`getBlockId got unexpected config variant: ${c}`);
  }
}

export function getEntrypointConcreteConfig(c: UserFlowEntryPointConfig) {
  return c.command || c.catch_all || c.regex;
}

export function getEntrypointId(c: UserFlowEntryPointConfig): string {
  const concreteConfig = getEntrypointConcreteConfig(c);
  if (concreteConfig) {
    return concreteConfig.entrypoint_id;
  } else {
    throw new Error(`getEntrypointId got unexpected config variant: ${c}`);
  }
}

export function flattenedFormFields(members: BranchingFormMemberConfig[]): FormFieldConfig[] {
  const fields: FormFieldConfig[] = [];
  for (const m of members) {
    if (m.field) {
      fields.push(m.field);
    } else if (m.branch) {
      fields.push(...flattenedFormFields(m.branch.members));
    }
  }
  return fields;
}

export function flattenedFormBranches(members: BranchingFormMemberConfig[]): FormBranchConfig[] {
  const res: FormBranchConfig[] = [];
  for (const m of members) {
    if (m.branch) {
      res.push(m.branch);
      res.push(...flattenedFormBranches(m.branch.members));
    }
  }
  return res;
}
