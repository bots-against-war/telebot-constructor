<script lang="ts">
  import { Stack, Button, Group, NativeSelect, CloseButton } from "@svelteuidev/core";
  import { createEventDispatcher } from "svelte";
  import { Plus } from "radix-icons-svelte";

  import FormField from "./FormField.svelte";

  import type { BranchingFormMemberConfig, FormBranchConfig, SingleSelectFormFieldConfig } from "../../../../api/types";
  import { getDefaultBaseFormFieldConfig, getDefaultFormFieldConfig, getFormFieldId } from "../utils";
  import { localizableTextToString } from "../../../utils";
  import { languageConfigStore } from "../../../stores";

  export let branch: FormBranchConfig;
  export let switchField: SingleSelectFormFieldConfig | null = null;

  const dispatch = createEventDispatcher<{ delete: null }>();

  let lastSwitchFieldBefore: (SingleSelectFormFieldConfig | null)[];
  $: {
    lastSwitchFieldBefore = [];
    let lastSeenSwitchField: SingleSelectFormFieldConfig | null = null;
    for (const m of branch.members) {
      lastSwitchFieldBefore.push(lastSeenSwitchField);
      if (m.field) {
        if (m.field.single_select) {
          lastSeenSwitchField = m.field.single_select;
        } else {
          lastSeenSwitchField = null;
        }
      }
    }
    lastSwitchFieldBefore.push(lastSeenSwitchField);
  }
</script>

<div class:conditional-branch-container={switchField !== null}>
  {#if switchField}
    <div class="delete-button-container">
      <CloseButton on:click={() => dispatch("delete")} />
    </div>
    <div class="conditional-branch-header">
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
  {/if}
  <Stack>
    {#each branch.members as member, idx}
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
          {#if lastSwitchFieldBefore[idx] !== null}
            <Button
              variant="outline"
              compact
              color="gray"
              on:click={() => {
                branch.members = branch.members.toSpliced(idx, 0, {
                  branch: {
                    members: [],
                    condition_match_value: undefined,
                  },
                });
              }}
            >
              <Plus slot="leftIcon" />
              Ветвь с условием
            </Button>
          {/if}
        </Group>
      {/if}

      {#if member.field}
        <FormField
          bind:fieldConfig={member.field}
          on:delete={() => {
            branch.members = branch.members.toSpliced(idx, 1);
          }}
        />
      {:else if member.branch}
        <svelte:self
          bind:branch={member.branch}
          switchField={lastSwitchFieldBefore[idx]}
          on:delete={() => {
            branch.members = branch.members.toSpliced(idx, 1);
          }}
        />
      {/if}
    {/each}

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
      {#if lastSwitchFieldBefore[branch.members.length] !== null}
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
                  condition_match_value: undefined,
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
  </Stack>
</div>

<style>
  div.conditional-branch-container {
    padding: 0.3em;
    padding-left: 1em;
    margin-left: 1em;
    border: 1px black solid;
    position: relative;
  }
  div.delete-button-container {
    position: absolute;
    right: 5px;
    top: 5px;
  }

  div.conditional-branch-header {
    width: 70%;
    padding: 0.5em;

    display: inline-flex;
    gap: 0.2em;
    align-items: baseline;
  }
</style>
