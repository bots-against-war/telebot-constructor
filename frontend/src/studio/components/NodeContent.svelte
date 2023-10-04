<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { ActionIcon, Group, Stack, Space, Flex, Divider } from "@svelteuidev/core";
  import { Pencil1, Cross1 } from "radix-icons-svelte";

  export let name: string;
  export let headerColor: string;

  const dispatch = createEventDispatcher<{ edit: null; delete: null }>();

  const actionIconProps = {
    color: "dark",
    size: "sm",
    variant: "hover",
  };
</script>

<Group
  spacing="xs"
  override={{
    backgroundColor: headerColor,
    borderRadius: "10px 10px 0 0;",
    padding: "8px",
    justifyContent: "space-between",
  }}
>
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
<Divider override={{ margin: 0 }} />
<div class="node-content">
  <slot />
</div>

<style>
  div.node-content {
    padding: 8px;
  }

  h3 {
    margin: 0.2em 0;
  }
</style>
