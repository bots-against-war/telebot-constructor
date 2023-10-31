<script lang="ts">
  import { Stack } from "@svelteuidev/core";
  import type { MenuBlock, MenuItem } from "../../../api/types";
  import NodeModalControls from "../../components/NodeModalControls.svelte";
  import LocalizableTextInput from "../../components/LocalizableTextInput.svelte";
  import SortableListInput from "../../components/SortableListInput.svelte";

  export let config: MenuBlock;
  export let onConfigUpdate: (newConfig: MenuBlock) => any;

  const editedConfig: MenuBlock = JSON.parse(JSON.stringify(config));

  function newMenuItem(): MenuItem {
    return {
      label: "",
      next_block_id: null,
    };
  }
</script>

<div>
  <h3>Меню</h3>
  <Stack>
    <LocalizableTextInput label="Текст" bind:value={editedConfig.menu.text} />
    <SortableListInput label="Варианты" bind:options={editedConfig.menu.items} optionConstructor={newMenuItem} />
  </Stack>
  <NodeModalControls on:save={() => onConfigUpdate(editedConfig)} />
</div>
