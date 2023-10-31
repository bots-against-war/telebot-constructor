<script lang="ts">
  import { Stack, Switch } from "@svelteuidev/core";
  import type { MenuBlock, MenuItem } from "../../../api/types";
  import NodeModalControls from "../../components/NodeModalControls.svelte";
  import LocalizableTextInput from "../../components/LocalizableTextInput.svelte";
  import SortableListInput from "../../components/SortableListInput.svelte";

  export let config: MenuBlock;
  export let onConfigUpdate: (newConfig: MenuBlock) => any;

  function saveConfig() {
    if (addBackButton) {
      editedConfig.menu.config.back_label = backButtonLabel;
    } else {
      editedConfig.menu.config.back_label = null;
    }
    onConfigUpdate(editedConfig);
  }

  const editedConfig: MenuBlock = JSON.parse(JSON.stringify(config));

  function newMenuItem(): MenuItem {
    return {
      label: "",
      next_block_id: null,
    };
  }

  let addBackButton = config.menu.config.back_label !== null;
  let backButtonLabel = config.menu.config.back_label || "";
</script>

<div>
  <h3>Меню</h3>
  <Stack>
    <LocalizableTextInput label="Текст" bind:value={editedConfig.menu.text} />
    <SortableListInput label="Пункты" bind:options={editedConfig.menu.items} optionConstructor={newMenuItem} />
    <Switch label="Возможность выйти на предыдущий уровень" bind:checked={addBackButton} />
    {#if addBackButton}
      <LocalizableTextInput label={'Кнопка "назад"'} bind:value={backButtonLabel} />
    {/if}
  </Stack>
  <NodeModalControls on:save={saveConfig} />
</div>
