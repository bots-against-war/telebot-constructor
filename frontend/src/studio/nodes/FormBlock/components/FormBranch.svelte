<script lang="ts">
  import { Select } from "flowbite-svelte";
  import type { ConditionMatchValue, FormBranchConfig, SingleSelectFormFieldConfig } from "../../../../api/types";
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
  export let switchFieldSelectedConditionValue: ConditionMatchValue | undefined = undefined;

  $: {
    branch.condition_match_value = switchFieldSelectedConditionValue;
  }

  // index among options of the switch field; used for color-coding
  let conditionMatchValueIdx: number | null = null;
  $: {
    if (switchField) {
      const foundOptionRes = switchField.options
        .map((option, idx) => {
          return { option, idx };
        })
        .find(({ option }) => option.id === switchFieldSelectedConditionValue);
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
  let currentSwitchFieldAt: (SingleSelectFormFieldConfig | null)[];
  let currentSwitchFieldIdxAt: (number | null)[];
  $: {
    currentSwitchFieldAt = [];
    currentSwitchFieldIdxAt = [];
    let currSwitch: SingleSelectFormFieldConfig | null = null;
    let currSwitchIdx: number | null = null;
    for (const [idx, m] of branch.members.entries()) {
      if (currSwitch && currSwitchIdx && currSwitch.options.length < idx - currSwitchIdx) {
        // invalidate current switch after # branches > # options
        [currSwitch, currSwitchIdx] = [null, null];
      }

      currentSwitchFieldAt.push(currSwitch);
      currentSwitchFieldIdxAt.push(currSwitchIdx);
      if (m.field) {
        if (m.field.single_select) {
          [currSwitch, currSwitchIdx] = [m.field.single_select, idx]; // found new current switch
        } else {
          [currSwitch, currSwitchIdx] = [null, null];
        }
      }
    }
    if (currSwitch && currSwitchIdx && currSwitch.options.length < branch.members.length - currSwitchIdx) {
      [currSwitch, currSwitchIdx] = [null, null];
    }
    currentSwitchFieldAt.push(currSwitch);
    currentSwitchFieldIdxAt.push(currSwitchIdx);
  }

  enum Direction {
    Down,
    Up,
  }
  function findFieldIdx(fromIdx: number, dir: Direction): number | null {
    const increment = dir == Direction.Down ? 1 : -1;
    let idx = fromIdx;
    while (idx > 0 && idx < branch.members.length) {
      idx = idx + increment;
      if (branch.members[idx].field !== null) return idx;
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
          bind:value={switchFieldSelectedConditionValue}
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
            currentSwitchField={currentSwitchFieldAt[idx]}
            on:add_field={() => {
              branch.members = branch.members.toSpliced(idx, 0, {
                field: getDefaultFormFieldConfig(getDefaultBaseFormFieldConfig(), "plain_text"),
              });
            }}
            on:add_branch={() => {
              branch.members = branch.members.toSpliced(idx, 0, {
                branch: {
                  members: [],
                  condition_match_value:
                    // @ts-expect-error
                    currentSwitchFieldAt[idx].options[idx - currentSwitchFieldIdxAt[idx] - 1].id,
                },
              });
            }}
          />

          <!-- actual branch member -->
          {#if member.field}
            <FormField
              isMovableUp={idx > 0}
              isMovableDown={idx < branch.members.length - 1 &&
                branch.members.some((member, memberIdx) => memberIdx > idx && member.field !== null)}
              bind:fieldConfig={member.field}
              on:delete={() => {
                branch.members = branch.members.toSpliced(idx, fieldMoveGroupSize(idx));
              }}
              on:moveup={() => {
                const newIdx = findFieldIdx(idx, Direction.Up);
                if (newIdx === null) return;
                const moveGroupSize = fieldMoveGroupSize(idx);
                const moveGroup = branch.members.slice(idx, idx + moveGroupSize);
                const newMembers = branch.members.toSpliced(idx, moveGroupSize);
                newMembers.splice(newIdx, 0, ...moveGroup);
                branch.members = newMembers;
              }}
              on:movedown={() => {
                const moveGroupSize = fieldMoveGroupSize(idx);
                const moveGroup = branch.members.slice(idx, idx + moveGroupSize);
                const newMembers = branch.members.toSpliced(idx, moveGroupSize);
                newMembers.splice(idx + moveGroupSize, 0, ...moveGroup);
                branch.members = newMembers;
              }}
            />
          {:else if member.branch}
            <svelte:self
              isMovableUp={idx > 0 && branch.members[idx - 1].branch !== null}
              isMovableDown={idx < branch.members.length - 1 && branch.members[idx + 1].branch !== null}
              bind:branch={member.branch}
              switchField={currentSwitchFieldAt[idx]}
              on:delete={() => {
                branch.members = branch.members.toSpliced(idx, 1);
              }}
            />
          {/if}
        {/each}

        <!-- at the end, buttons to add stuff after everything -->
        <AddBranchMemberButtons
          allowAddField
          currentSwitchField={currentSwitchFieldAt[branch.members.length]}
          on:add_field={() => {
            branch.members = [
              ...branch.members,
              {
                field: getDefaultFormFieldConfig(getDefaultBaseFormFieldConfig(), "plain_text"),
              },
            ];
          }}
          on:add_branch={() => {
            const idx = branch.members.length;
            branch.members = [
              ...branch.members,
              {
                branch: {
                  members: [],
                  condition_match_value:
                    // @ts-expect-error
                    currentSwitchFieldAt[idx].options[idx - currentSwitchFieldIdxAt[idx] - 1].id,
                },
              },
            ];
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
