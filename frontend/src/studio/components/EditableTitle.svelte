<script lang="ts">
  import { Group, ActionIcon, Title, Input } from "@svelteuidev/core";

  import { Pencil1, Check, Cross1 } from "radix-icons-svelte";

  export let title: string;

  let isEditing = false;
  let editedTitle = title;
</script>

<Group>
  {#if isEditing}
    <Title>
      <Input bind:value={editedTitle} />
    </Title>
    <Group override={{ gap: "0" }}>
      <ActionIcon
        on:click={() => {
          title = editedTitle;
          isEditing = false;
        }}
      >
        <Check />
      </ActionIcon>
      <ActionIcon on:click={() => (isEditing = false)}>
        <Cross1 />
      </ActionIcon>
    </Group>
  {:else}
    <Title>
      {title}
    </Title>
    <ActionIcon on:click={() => (isEditing = true)}>
      <Pencil1 />
    </ActionIcon>
  {/if}
</Group>
