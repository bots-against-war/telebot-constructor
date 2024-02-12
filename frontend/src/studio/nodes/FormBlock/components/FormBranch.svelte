<script lang="ts">
  import { Button, Select } from "flowbite-svelte";
  import { type ButtonProps } from "flowbite-svelte/Button.svelte";
  import { CloseOutline, PlusOutline } from "flowbite-svelte-icons";
  import { createEventDispatcher } from "svelte";
  import type { FormBranchConfig, SingleSelectFormFieldConfig } from "../../../../api/types";
  import ActionIcon from "../../../../components/ActionIcon.svelte";
  import { languageConfigStore } from "../../../stores";
  import { localizableTextToString } from "../../../utils";
  import { backgroundColor, borderColor, generateHue } from "../colors";
  import { getDefaultBaseFormFieldConfig, getDefaultFormFieldConfig } from "../utils";
  import FormField from "./FormField.svelte";

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

  const buttonProps: ButtonProps = {
    color: "light",
    size: "sm",
    outline: true,
  };
</script>

<div
  class:conditional-branch-container={switchField !== null}
  style={branchHue ? `border-color: ${borderColor(branchHue)};` : ""}
>
  {#if switchField}
    <div class="conditional-branch-header" style={branchHue ? `background-color: ${backgroundColor(branchHue)};` : ""}>
      <div class="flex flex-row justify-between">
        <div class="conditional-branch-condition">
          Если <strong>{switchField.name}</strong> =
          <Select
            items={switchField.options.map((o) => {
              return {
                name: localizableTextToString(o.label, $languageConfigStore),
                value: o.id,
              };
            })}
            bind:value={branch.condition_match_value}
          />
        </div>
        <ActionIcon icon={CloseOutline} on:click={() => dispatch("delete")} />
      </div>
    </div>
  {/if}
  <div class:conditional-branch-body={switchField !== null}>
    <div class="flex flex-col gap-2">
      <!-- each block is keyed so that it is correctly modified on inserting new members -->
      {#each branch.members as member, idx (member.field ? member.field : member.branch)}
        <!-- buttons that add stuff before the current member -->
        {#if member.field}
          <div class="flex flex-row justify-center gap-2">
            <Button
              on:click={() => {
                branch.members = branch.members.toSpliced(idx, 0, {
                  field: getDefaultFormFieldConfig(getDefaultBaseFormFieldConfig(), "plain_text"),
                });
              }}
              {...buttonProps}
            >
              <PlusOutline size="sm" class="mr-2" />
              Поле
            </Button>
            {#if currentSwitchFieldAt[idx] !== null}
              <Button
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
                {...buttonProps}
              >
                <PlusOutline size="sm" class="mr-2" />
                <span>
                  Ветвь с условием на "{(currentSwitchFieldAt[idx] || { name: "" }).name}"
                </span>
              </Button>
            {/if}
          </div>
        {/if}

        <!-- actual branch member -->
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

      <!-- at the end, buttons to add stuff after everything -->
      <div class="flex flex-row justify-center gap-2">
        <Button
          on:click={() => {
            branch.members = [
              ...branch.members,
              {
                field: getDefaultFormFieldConfig(getDefaultBaseFormFieldConfig(), "plain_text"),
              },
            ];
          }}
          {...buttonProps}
        >
          <PlusOutline size="sm" class="mr-2" />
          Поле
        </Button>
        {#if currentSwitchFieldAt[branch.members.length] !== null}
          <Button
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
            {...buttonProps}
          >
            <PlusOutline size="sm" class="mr-2" />
            <span>
              Ветвь с условием на "{(currentSwitchFieldAt[branch.members.length] || { name: "" }).name}"
            </span>
          </Button>
        {/if}
      </div>
    </div>
  </div>
</div>

<!-- TODO: move at least some of the styles to tailwind classes -->
<style>
  div.conditional-branch-container {
    border-left: 2px white solid;
    border-bottom: 2px white solid;
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
