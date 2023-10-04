<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { ActionIcon, Group, Stack, Space, Flex } from "@svelteuidev/core";
  import { Pencil1, Cross1 } from "radix-icons-svelte";

  export let name: string;

  const dispatch = createEventDispatcher<{ edit: null; delete: null }>();

  const actionIconProps = {
    color: "dark",
    size: "sm",
    variant: "hover",
  };
</script>

<div class="node-content">
  <Stack align="strech" justify="space-between" spacing="none">
    <Group spacing="xs">
      <h3>{name}</h3>
      <Space w="md" />
      <Flex>
        <ActionIcon {...actionIconProps} on:click={() => dispatch("edit")}>
          <Pencil1 />
        </ActionIcon>
        <ActionIcon {...actionIconProps} on:click={() => dispatch("delete")}>
          <Cross1 />
        </ActionIcon>
      </Flex>
    </Group>
    <slot />
  </Stack>
</div>

<style>
  div.node-content {
    margin: 8px;
  }

  h3 {
    margin: 0.2em 0;
  }
</style>
