<script lang="ts">
  import { Stack, Button, Group } from "@svelteuidev/core";
  import { Plus } from "radix-icons-svelte";

  import FormField from "./FormField.svelte";

  import type { BranchingFormMemberConfig, FormBranchConfig, SingleSelectFormFieldConfig } from "../../../../api/types";
  import { getDefaultBaseFormFieldConfig, getDefaultFormFieldConfig, getFormFieldId } from "../utils";

  export let branch: FormBranchConfig;
  export let parentBranchMembers: BranchingFormMemberConfig[];
  export let idxInParentBranch: number;

  let foundSwitchField: boolean = false;
  let switchSingleSelectField: SingleSelectFormFieldConfig;
  $: {
    foundSwitchField = false;
    for (let previousFieldIdx = idxInParentBranch - 1; previousFieldIdx >= 0; previousFieldIdx--) {
      const maybeSwitchSingleSelectField = (parentBranchMembers[previousFieldIdx].field || {}).single_select;
      if (maybeSwitchSingleSelectField) {
        switchSingleSelectField = maybeSwitchSingleSelectField;
        foundSwitchField = true;
        break;
      }
    }
  }
</script>

<div class:conditional-branch-container={foundSwitchField}>
  {#if switchSingleSelectField}
    <!-- TODO: selector -->
  {/if}
  <Stack>
    {#each branch.members as member, idx}
      {#if member.field}
        <FormField
          bind:fieldConfig={member.field}
          on:delete={() => {
            const newMembers = branch.members.filter(
              (m) => !(m.field && member.field && getFormFieldId(m.field) === getFormFieldId(member.field)),
            );
            branch.members = newMembers;
          }}
        />
      {:else if member.branch}
        <svelte:self bind:branch={member.branch} parentBranchMembers={branch.members} idxInParentBranch={idx} />
      {/if}
      <Group position="center">
        <Button
          variant="outline"
          compact
          color="gray"
          on:click={() => {
            branch.members = branch.members.toSpliced(idx + 1, 0, {
              field: getDefaultFormFieldConfig(getDefaultBaseFormFieldConfig(), "plain_text"),
            });
          }}
        >
          <Plus slot="leftIcon" />
          Поле
        </Button>
        {#if member.field && member.field.single_select}
          <Button
            variant="outline"
            compact
            color="gray"
            on:click={() => {
              branch.members = [
                ...branch.members,
                {
                  branch: {
                    members: [],
                    condition_match_value: null,
                  },
                },
              ];
            }}
          >
            <Plus slot="leftIcon" />
            Ветвь с условием
          </Button>
        {/if}
      </Group>
    {/each}
    {#if branch.members.length === 0}
      <Button
        variant="outline"
        compact
        color="gray"
        on:click={() => {
          branch.members = [
            {
              field: getDefaultFormFieldConfig(getDefaultBaseFormFieldConfig(), "plain_text"),
            },
          ];
        }}
      >
        <Plus slot="leftIcon" />
        Добавить поле
      </Button>
    {/if}
  </Stack>
</div>

<style>
  div.conditional-branch-container {
    padding-left: 1em;
    margin-left: 1em;
    border-left: 1px black solid;
  }
</style>
