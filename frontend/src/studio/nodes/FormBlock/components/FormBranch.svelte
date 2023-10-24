<script lang="ts">
  import { Stack, Container, ActionIcon } from "@svelteuidev/core";
  import { Plus } from "radix-icons-svelte";

  import FormField from "./FormField.svelte";

  import type { BranchingFormMemberConfig } from "../../../../api/types";
  import { getFormFieldId } from "../utils";

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
  <Container>
    <ActionIcon
      variant="outline"
      on:click={() => {
        members = [
          ...members,
          {
            field: {
              plain_text: {
                id: `form_field_${crypto.randomUUID()}`,
                name: "",
                prompt: "",
                is_required: true,
                result_formatting: "auto",
                is_long_text: false,
                empty_text_error_msg: "",
              },
            },
          },
        ];
      }}
    >
      <Plus />
    </ActionIcon>
  </Container>
</Stack>
