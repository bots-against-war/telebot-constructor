<script lang="ts">
  import { Stack, Container, ActionIcon } from "@svelteuidev/core";
  import { Plus } from "radix-icons-svelte";
  import FormField from "./FormField.svelte";
  import type { BranchingFormMemberConfig } from "../../../../api/types";

  export let members: BranchingFormMemberConfig[];
</script>

<Stack>
  <Stack>
    {#each members as member}
      {#if member.field}
        <FormField bind:fieldConfig={member.field} />
      {:else if member.branch}
        <svelte:self bind:members={member.branch.members} />
      {/if}
    {/each}
  </Stack>
  <Container>
    <ActionIcon variant="outline"><Plus /></ActionIcon>
  </Container>
</Stack>
