<script lang="ts">
  import { Select, Toggle } from "flowbite-svelte";
  import type { MenuBlock, MenuItem, MenuMechanism } from "../../../api/types";
  import InputWrapper from "../../../components/inputs/InputWrapper.svelte";
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

  interface MenuMechanismSelectItem {
    name: string;
    value: MenuMechanism;
  }
  const menuMechanismSelectItems: MenuMechanismSelectItem[] = [
    {
      name: "Под сообщением",
      value: "inline_buttons",
    },
    {
      name: "Кастомная клавиатура",
      value: "reply_keyboard",
    },
  ];
</script>

<NodeModalBody title={NODE_TITLE.menu}>
  <LocalizableTextInput
    label="Текст"
    required
    bind:value={editedConfig.menu.text}
    maxCharacters={TELEGRAM_MAX_MESSAGE_LENGTH_CHARS}
    on:languageChanged={(event) => {
      selectedLang = event.detail;
    }}
  />
  <InputWrapper label="Тип кнопок" required={false}>
    <Select placeholder="" items={menuMechanismSelectItems} bind:value={editedConfig.menu.config.mechanism} />
    <div class="text-sm text-gray-600">
      {#if editedConfig.menu.config.mechanism == "inline_buttons"}
        <a target="_blank" href="https://core.telegram.org/bots/features#inline-keyboards">Кнопки под сообщением</a>
        хорошо подходят для небольших, динамичных меню. Текст сообщения обновляется при навигации по меню. Telegram автоматически
        деактивирует кнопки через несколько дней после отправки, поэтому этот тип не подойдёт для меню, которое должно использоваться
        в течение долгого времени.
      {:else}
        <a target="_blank" href="https://core.telegram.org/bots/features#keyboards">Кастомная клавиатура</a> подходит для
        длинных разветвленных диалоговых схем. Каждый новый уровень отправляется новым сообщением.
      {/if}
    </div>
  </InputWrapper>
  <SortableListInput
    label="Кнопки"
    bind:options={editedConfig.menu.items}
    optionConstructor={newMenuItem}
    {selectedLang}
  />
  <Toggle bind:checked={addBackButton}>Выход на предыдущий уровень</Toggle>
  {#if addBackButton}
    <LocalizableTextInput
      required
      label={'Кнопка "назад"'}
      bind:value={backButtonLabel}
      maxCharacters={TELEGRAM_MAX_MESSAGE_LENGTH_CHARS}
    />
  {/if}
  <NodeModalControls on:save={saveConfig} />
</NodeModalBody>
