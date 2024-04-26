<script lang="ts">
  import { Select } from "flowbite-svelte";
  import type { BranchingFormMemberConfig, FormBranchConfig, SingleSelectFormFieldConfig } from "../../../../api/types";
  import { languageConfigStore } from "../../../stores";
  import { localizableTextToString } from "../../../utils";
  import { backgroundColor, borderColor, generateHue } from "../colors";
  import { getDefaultBaseFormFieldConfig, getDefaultFormFieldConfig } from "../utils";
  import FormField from "./FormField.svelte";
  import FormMemberFrame from "./FormMemberFrame.svelte";

  import AddBranchMemberButtons from "./AddBranchMemberButtons.svelte";

  export let branch: FormBranchConfig;
  export let isMovableUp: boolean;
  export let isMovableDown: boolean;
  export let switchField: SingleSelectFormFieldConfig | null = null;

  // index among options of the switch field; used for color-coding
  let conditionMatchValueIdx: number | null = null;
  $: {
    if (switchField) {
      const foundOptionRes = switchField.options
        .map((option, idx) => {
          return { option, idx };
        })
        .find(({ option }) => option.id === branch.condition_match_value);
      if (foundOptionRes) conditionMatchValueIdx = foundOptionRes.idx;
    }
  }

  let branchHue: number | null = null;
  $: branchHue =
    switchField !== null && conditionMatchValueIdx !== null
      ? generateHue(switchField.id, conditionMatchValueIdx)
      : null;

  // each (sub)branch requires a previous Single Select field as a switch (condition)
  // here we find in advance (and update with reactive block), which single select
  // field acts as switch for any given position in the members array
  // these arrays are one item longer than branch.members to account for adding stuff
  // after the last one member (e.g. before the virtual one-after-last)

  interface SwitchField {
    config: SingleSelectFormFieldConfig;
    idx: number;
    currentBranches: number;
  }

  function isAcceptingBranches(sf: SwitchField | undefined | null): boolean {
    if (!sf) return false;
    else return sf.currentBranches < sf.config.options.length;
  }

  function newBranchMemberAt(idx: number): BranchingFormMemberConfig | null {
    const sf = switchFieldFor[idx];
    if (!sf) return null;
    const usedConditionMatchValues = branch.members
      .map((m) => m.branch)
      .filter<FormBranchConfig>(
        (b, branchIdx): b is FormBranchConfig =>
          Boolean(b) && branchIdx > sf.idx && switchFieldFor[branchIdx]?.idx === sf.idx,
      )
      .map((b) => b.condition_match_value);
    const freeConditionMatchValues = sf.config.options
      .map((o) => o.id)
      .filter((cmv) => !usedConditionMatchValues.includes(cmv));
    if (freeConditionMatchValues.length === 0) return null;
    return {
      branch: {
        members: [],
        condition_match_value: freeConditionMatchValues[0],
      },
    };
  }

  let switchFieldFor: (SwitchField | null)[];
  $: {
    switchFieldFor = [];
    let lastSwitchField: SwitchField | null = null;
    for (const [idx, member] of branch.members.entries()) {
      switchFieldFor.push(lastSwitchField);
      if (member.field) {
        if (member.field.single_select) {
          lastSwitchField = { config: member.field.single_select, idx, currentBranches: 0 };
        } else {
          lastSwitchField = null;
        }
      } else if (member.branch) {
        if (lastSwitchField) {
          lastSwitchField.currentBranches += 1;
        } else {
          console.error("Error: found branch, but no last switch field", branch.members);
        }
      }
    }
    switchFieldFor.push(lastSwitchField);
  }

  enum Direction {
    Down = "down",
    Up = "up",
  }
  function increment(dir: Direction) {
    switch (dir) {
      case Direction.Down:
        return 1;
      case Direction.Up:
        return -1;
    }
  }
  function findNextFieldIdx(fromIdx: number, dir: Direction): number | null {
    const incr = increment(dir);
    let idx = fromIdx + incr;
    while (idx >= 0 && idx <= branch.members.length - 1) {
      if (branch.members[idx].field !== null) return idx;
      idx = idx + incr;
    }
    return null;
  }

  function fieldMoveGroupSize(idx: number): number {
    if (!branch.members[idx]?.field) return 1;
    let moveGroupEndIdx = idx + 1;
    // including branches following the switch into "move group"
    while (moveGroupEndIdx <= branch.members.length - 1 && branch.members[moveGroupEndIdx].branch) moveGroupEndIdx += 1;
    return moveGroupEndIdx - idx;
  }

  function moveField(idx: number, dir: Direction) {
    let targetIdx = findNextFieldIdx(idx, dir);
    if (dir === Direction.Down && targetIdx) {
      // since we're inserting *before* the next field, for "down" direction,
      // we actually need to find the second field from the starting one
      targetIdx = findNextFieldIdx(targetIdx, Direction.Down);
    }

    const moveGroupSize = fieldMoveGroupSize(idx);
    const moveGroup = branch.members.slice(idx, idx + moveGroupSize);
    const newMembers = branch.members.toSpliced(idx, moveGroupSize);
    if (targetIdx === null) {
      targetIdx = dir === Direction.Up ? 0 : branch.members.length;
    } else if (dir === Direction.Down) {
      // after splicing everything moved up, we need to adjust the idx
      targetIdx -= moveGroupSize;
    }
    newMembers.splice(targetIdx, 0, ...moveGroup);

    console.debug(
      `Moving field #${idx} ${dir}, target idx = ${targetIdx}, moveGroupSize = ${moveGroupSize}`,
      moveGroup,
      newMembers,
    );
    branch.members = newMembers;
  }

  function moveBranch(idx: number, dir: Direction) {
    const targetIdx = idx + increment(dir);
    if (branch.members[targetIdx].field) return;
    const moved = branch.members[idx];
    const newMembers = branch.members.toSpliced(idx, 1);
    newMembers.splice(targetIdx, 0, moved);
    console.debug(`Moving branch #${idx} ${dir}, target idx = ${targetIdx}`, newMembers);
    branch.members = newMembers;
  }
</script>

<FormMemberFrame {isMovableUp} {isMovableDown} isDeletable={switchField !== null} on:delete on:moveup on:movedown>
  <!-- if the current branch is conditional, render conditional branch header, showing what option it is conditioned on -->
  <div
    class:conditional-branch-container={switchField !== null}
    style={branchHue ? `border-color: ${borderColor(branchHue)};` : ""}
  >
    {#if switchField}
      <div
        class="flex flex-row p-4 items-center justify-between gap-2"
        style={branchHue ? `background-color: ${backgroundColor(branchHue)};` : ""}
      >
        <strong>{switchField.name}</strong>
        <Select
          placeholder=""
          items={switchField.options.map((o) => {
            return {
              name: localizableTextToString(o.label, $languageConfigStore),
              value: o.id,
            };
          })}
          bind:value={branch.condition_match_value}
        />
      </div>
    {/if}
    <!-- the actual branch body: sequence of fields and possible sub-branches -->
    <div class:conditional-branch-body={switchField !== null}>
      <div class="flex flex-col gap-2">
        <!-- each block is keyed so that it is correctly modified on inserting new members -->
        {#each branch.members as member, idx (member.field ? member.field : member.branch)}
          <!-- buttons that add stuff before the current member -->
          <AddBranchMemberButtons
            allowAddField={member.field !== null}
            currentSwitchField={isAcceptingBranches(switchFieldFor[idx]) ? switchFieldFor[idx]?.config : null}
            on:add_field={() => {
              branch.members = branch.members.toSpliced(idx, 0, {
                field: getDefaultFormFieldConfig(getDefaultBaseFormFieldConfig(), "plain_text"),
              });
            }}
            on:add_branch={() => {
              const newMember = newBranchMemberAt(idx);
              if (newMember) {
                branch.members = branch.members.toSpliced(idx, 0, newMember);
              }
            }}
          />

          <!-- actual branch member -->
          {#if member.field}
            <!-- regular field -->
            <FormField
              isMovableUp={idx > 0}
              isMovableDown={idx < branch.members.length - 1 &&
                branch.members.some((member, memberIdx) => memberIdx > idx && member.field !== null)}
              bind:fieldConfig={member.field}
              on:delete={() => {
                branch.members = branch.members.toSpliced(idx, fieldMoveGroupSize(idx));
              }}
              on:moveup={() => moveField(idx, Direction.Up)}
              on:movedown={() => moveField(idx, Direction.Down)}
            />
          {:else if member.branch}
            <!-- sub-branch, rendering it with recursive call to svelte:self -->
            <svelte:self
              isMovableUp={idx > 0 && branch.members[idx - 1].branch !== null}
              isMovableDown={idx < branch.members.length - 1 && branch.members[idx + 1].branch !== null}
              bind:branch={member.branch}
              switchField={switchFieldFor[idx]?.config}
              on:delete={() => {
                branch.members = branch.members.toSpliced(idx, 1);
              }}
              on:moveup={() => moveBranch(idx, Direction.Up)}
              on:movedown={() => moveBranch(idx, Direction.Down)}
            />
          {/if}
        {/each}

        <!-- at the end, buttons to add stuff after everything -->
        <AddBranchMemberButtons
          allowAddField
          currentSwitchField={switchFieldFor[branch.members.length]?.config}
          on:add_field={() => {
            branch.members = [
              ...branch.members,
              {
                field: getDefaultFormFieldConfig(getDefaultBaseFormFieldConfig(), "plain_text"),
              },
            ];
          }}
          on:add_branch={() => {
            const newMember = newBranchMemberAt(branch.members.length);
            if (newMember) {
              branch.members = [...branch.members, newMember];
            }
          }}
        />
      </div>
    </div>
  </div>
</FormMemberFrame>

<!-- TODO: move at least some of the styles to tailwind classes -->
<style>
  div.conditional-branch-container {
    border-left: 2px white solid;
    border-bottom: 2px white solid;
    border-right: 2px white solid;
  }
  div.conditional-branch-body {
    padding: 10px;
  }
</style>
