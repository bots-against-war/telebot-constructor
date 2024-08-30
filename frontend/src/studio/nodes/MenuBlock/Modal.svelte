<script lang="ts">
  import { Toggle } from "flowbite-svelte";
  import type { MenuBlock, MenuItem } from "../../../api/types";
  import { TELEGRAM_MAX_MESSAGE_LENGTH_CHARS } from "../../../constants";
  import LocalizableTextInput from "../../components/LocalizableTextInput.svelte";
  import NodeModalBody from "../../components/NodeModalBody.svelte";
  import NodeModalControls from "../../components/NodeModalControls.svelte";
  import SortableListInput from "../../components/SortableListInput.svelte";
  import { languageConfigStore } from "../../stores";
  import { clone } from "../../utils";
  import { NODE_TITLE } from "../display";

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

  const editedConfig: MenuBlock = clone(config);

  function newMenuItem(): MenuItem {
    return {
      label: "",
      next_block_id: null,
    };
  }

  let addBackButton = config.menu.config.back_label !== null;
  let backButtonLabel = config.menu.config.back_label || "";

  let selectedLang: string | null = null;
  selectedLang = $languageConfigStore ? $languageConfigStore.supportedLanguageCodes[0] : null;
</script>

<NodeModalBody title={NODE_TITLE.menu}>
  <LocalizableTextInput
    label="Текст"
    bind:value={editedConfig.menu.text}
    maxCharacters={TELEGRAM_MAX_MESSAGE_LENGTH_CHARS}
    on:languageChanged={(event) => {
      selectedLang = event.detail;
    }}
  />
  <SortableListInput
    label="Кнопки"
    bind:options={editedConfig.menu.items}
    optionConstructor={newMenuItem}
    {selectedLang}
  />
  <Toggle bind:checked={addBackButton}>Возможность вернуться назад</Toggle>
  {#if addBackButton}
    <LocalizableTextInput
      label={'Кнопка "назад"'}
      bind:value={backButtonLabel}
      maxCharacters={TELEGRAM_MAX_MESSAGE_LENGTH_CHARS}
    />
  {/if}
  <NodeModalControls on:save={saveConfig} />
</NodeModalBody>
