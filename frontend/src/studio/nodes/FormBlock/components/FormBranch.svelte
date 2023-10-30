<script lang="ts">
  import { Stack, Button, Group, NativeSelect, CloseButton } from "@svelteuidev/core";
  import { createEventDispatcher } from "svelte";
  import { Plus } from "radix-icons-svelte";

  import FormField from "./FormField.svelte";

  import type { FormBranchConfig, SingleSelectFormFieldConfig } from "../../../../api/types";
  import { getDefaultBaseFormFieldConfig, getDefaultFormFieldConfig } from "../utils";
  import { localizableTextToString } from "../../../utils";
  import { languageConfigStore } from "../../../stores";
  import { backgroundColor, borderColor, generateHue } from "../colors";

  export let branch: FormBranchConfig;
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

  const dispatch = createEventDispatcher<{ delete: null }>();

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
</script>

<div
  class:conditional-branch-container={switchField !== null}
  style={branchHue ? `border-color: ${borderColor(branchHue)};` : ""}
>
  {#if switchField}
    <div class="conditional-branch-header" style={branchHue ? `background-color: ${backgroundColor(branchHue)};` : ""}>
      <Group position="apart">
        <div class="conditional-branch-condition">
          Если <strong>{switchField.name}</strong> =
          <NativeSelect
            override={{ display: "inline", flexGrow: "10" }}
            data={switchField.options.map((o) => {
              return {
                label: localizableTextToString(o.label, $languageConfigStore),
                value: o.id,
              };
            })}
            bind:value={branch.condition_match_value}
          />
        </div>
        <CloseButton on:click={() => dispatch("delete")} />
      </Group>
    </div>
  {/if}
  <div class:conditional-branch-body={switchField !== null}>
    <Stack>
      <!-- each block is keyed so that it is correctly modified on inserting new members -->
      {#each branch.members as member, idx (member.field ? member.field : member.branch)}
        <!-- buttons add stuff BEFORE the current member -->
        {#if member.field}
          <Group position="center">
            <Button
              variant="outline"
              compact
              color="gray"
              on:click={() => {
                branch.members = branch.members.toSpliced(idx, 0, {
                  field: getDefaultFormFieldConfig(getDefaultBaseFormFieldConfig(), "plain_text"),
                });
              }}
            >
              <Plus slot="leftIcon" />
              Поле
            </Button>
            {#if currentSwitchFieldAt[idx] !== null}
              <Button
                variant="outline"
                compact
                color="gray"
                on:click={() => {
                  branch.members = branch.members.toSpliced(idx, 0, {
                    branch: {
                      members: [],
                      condition_match_value:
                        // @ts-expect-error
                        currentSwitchFieldAt[idx].options[idx - currentSwitchFieldIdxAt[idx] - 1].id,
                    },
                  });
                }}
              >
                <Plus slot="leftIcon" />
                <span>
                  Ветвь с условием на "{(currentSwitchFieldAt[idx] || { name: "" }).name}"
                </span>
              </Button>
            {/if}
          </Group>
        {/if}

        {#if member.field}
          <FormField
            bind:fieldConfig={member.field}
            on:delete={() => {
              let firstIdxToLeave = idx + 1;
              // deleting branches with the switch, if present
              while (firstIdxToLeave <= branch.members.length - 1 && branch.members[firstIdxToLeave].branch)
                firstIdxToLeave += 1;
              branch.members = branch.members.toSpliced(idx, firstIdxToLeave - idx);
            }}
          />
        {:else if member.branch}
          <svelte:self
            bind:branch={member.branch}
            switchField={currentSwitchFieldAt[idx]}
            on:delete={() => {
              branch.members = branch.members.toSpliced(idx, 1);
            }}
          />
        {/if}
      {/each}

      <!-- additional buttons to add stuff AFTER everything (e.g. "before" one-past-last element) -->
      <Group position="center">
        <Button
          variant="outline"
          compact
          color="gray"
          on:click={() => {
            branch.members = [
              ...branch.members,
              {
                field: getDefaultFormFieldConfig(getDefaultBaseFormFieldConfig(), "plain_text"),
              },
            ];
          }}
        >
          <Plus slot="leftIcon" />
          Поле
        </Button>
        {#if currentSwitchFieldAt[branch.members.length] !== null}
          <Button
            variant="outline"
            compact
            color="gray"
            on:click={() => {
              const idx = branch.members.length;
              branch.members = [
                ...branch.members,
                {
                  branch: {
                    members: [],
                    // @ts-expect-error
                    condition_match_value: currentSwitchFieldAt[idx].options[idx - currentSwitchFieldIdxAt[idx] - 1].id,
                  },
                },
              ];
            }}
          >
            <Plus slot="leftIcon" />
            <span>
              Ветвь с условием на "{(currentSwitchFieldAt[branch.members.length] || { name: "" }).name}"
            </span>
          </Button>
        {/if}
      </Group>
    </Stack>
  </div>
</div>

<style>
  div.conditional-branch-container {
    border-left: 3px rgb(206, 212, 218) solid;
  }

  div.conditional-branch-header {
    padding: 15px;
  }

  div.conditional-branch-body {
    padding: 10px;
  }

  div.conditional-branch-condition {
    width: 70%;
    display: inline-flex;
    gap: 0.2em;
    align-items: center;
  }
</style>
