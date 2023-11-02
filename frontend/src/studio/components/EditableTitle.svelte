<script lang="ts">
  import { ActionIcon, Group, Input, Space, Title } from "@svelteuidev/core";
  import { CheckOutline, CloseOutline, PenOutline } from "flowbite-svelte-icons";
  import EllipsisText from "../../components/internal/EllipsisText.svelte";

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
        <CheckOutline />
      </ActionIcon>
      <Space w="md" />
      <ActionIcon on:click={() => (isEditing = false)}>
        <CloseOutline />
      </ActionIcon>
    </Group>
  {:else}
    <EllipsisText maxWidth="300px" size={24}>
      {title}
    </EllipsisText>
    <ActionIcon on:click={() => (isEditing = true)}>
      <PenOutline />
    </ActionIcon>
  {/if}
</Group>
