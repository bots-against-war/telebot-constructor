<script lang="ts">
  import { t } from "svelte-i18n";
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

  // decomposing MenuMechanism enum into button type + mutable/immutable (for inline only)
  type ButtonType = "inline" | "reply";

  function saveConfig() {
    if (selectedButtonType == "reply") {
      editedConfig.menu.config.mechanism = "reply_keyboard";
    } else if (mutableInlineButtons) {
      editedConfig.menu.config.mechanism = "inline_buttons";
    } else {
      editedConfig.menu.config.mechanism = "inline_buttons_immutable";
    }

    if (addBackButton) {
      editedConfig.menu.config.back_label = backButtonLabel;
    } else {
      editedConfig.menu.config.back_label = null;
    }

    onConfigUpdate(editedConfig);
  }

  const editedConfig: MenuBlock = clone(config);
  editedConfig.menu.markup = "markdown";

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

  let selectedButtonType: ButtonType = config.menu.config.mechanism === "reply_keyboard" ? "reply" : "inline";
  let mutableInlineButtons = config.menu.config.mechanism !== "inline_buttons_immutable";

  interface ButtonTypeSelectItem {
    name: string;
    value: ButtonType;
  }
  const buttonTypeSelectItems: ButtonTypeSelectItem[] = [
    {
      name: $t("studio.menu.inline_button_label"),
      value: "inline",
    },
    {
      name: $t("studio.menu.reply_button_label"),
      value: "reply",
    },
  ];
</script>

<NodeModalBody title={NODE_TITLE.menu}>
  <LocalizableTextInput
    label={$t("studio.menu.message_text_label")}
    required
    markdown
    bind:value={editedConfig.menu.text}
    maxCharacters={TELEGRAM_MAX_MESSAGE_LENGTH_CHARS}
    on:languageChanged={(event) => {
      selectedLang = event.detail;
    }}
  />
  <InputWrapper label={$t("studio.menu.button_type_label")} required={false}>
    <Select placeholder="" items={buttonTypeSelectItems} bind:value={selectedButtonType} />
    <div class="text-sm text-gray-600">
      {#if selectedButtonType == "inline"}
        <Toggle class="my-2" size="small" bind:checked={mutableInlineButtons}>
          {$t("studio.menu.inline_mutable")}
        </Toggle>
        <p>
          {$t("studio.menu.inline_button_help")}
        </p>
      {:else}
        {$t("studio.menu.reply_button_help")}
      {/if}
    </div>
  </InputWrapper>
  <SortableListInput
    label={$t("studio.menu.buttons_label")}
    bind:options={editedConfig.menu.items}
    optionConstructor={newMenuItem}
    {selectedLang}
  />
  <Toggle bind:checked={addBackButton}>{$t("studio.menu.go_up")}</Toggle>
  {#if addBackButton}
    <LocalizableTextInput
      required
      label={$t("studio.menu.back_button_label")}
      bind:value={backButtonLabel}
      maxCharacters={TELEGRAM_MAX_MESSAGE_LENGTH_CHARS}
    />
  {/if}
  <NodeModalControls on:save={saveConfig} />
</NodeModalBody>
