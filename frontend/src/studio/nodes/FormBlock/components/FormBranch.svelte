<script lang="ts">
  import { Stack, Container, Button } from "@svelteuidev/core";
  import { Plus } from "radix-icons-svelte";

  import FormField from "./FormField.svelte";

  import type { BranchingFormMemberConfig } from "../../../../api/types";
  import { getDefaultBaseFormFieldConfig, getDefaultFormFieldConfig, getFormFieldId } from "../utils";

  export let members: BranchingFormMemberConfig[];
</script>

<Stack>
  <Stack>
    {#each members as member}
      {#if member.field}
        <FormField
          bind:fieldConfig={member.field}
          on:delete={() => {
            const newMembers = members.filter(
              // @ts-expect-error
              (mc) => !(mc.field && getFormFieldId(mc.field) === getFormFieldId(member.field)),
            );
            members = newMembers;
          }}
        />
      {:else if member.branch}
        <svelte:self bind:members={member.branch.members} />
      {/if}
    {/each}
  </Stack>
  <Button
    variant="outline"
    compact
    color="gray"
    on:click={() => {
      members = [
        ...members,
        {
          field: getDefaultFormFieldConfig(getDefaultBaseFormFieldConfig(), "plain_text"),
        },
      ];
    }}
  >
    <Plus slot="leftIcon" />
    Добавить поле
  </Button>
</Stack>
