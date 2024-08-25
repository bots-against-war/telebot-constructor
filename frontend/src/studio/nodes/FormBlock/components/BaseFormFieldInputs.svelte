<script lang="ts">
  import { Toggle } from "flowbite-svelte";
  import type { BaseFormFieldConfig } from "../../../../api/types";
  import EditableText from "../../../../components/inputs/EditableText.svelte";
  import LocalizableTextInput from "../../../components/LocalizableTextInput.svelte";
  import { languageConfigStore } from "../../../stores";
  import { localizableTextToString } from "../../../utils";
  import { getRandomContent as getRandomFormExampleContent } from "../content";
  import { TELEGRAM_MAX_MESSAGE_LENGTH_CHARS } from "../../../../constants";
  export let config: BaseFormFieldConfig;

  let exampleContent = getRandomFormExampleContent();
  let hasEditedFieldName = config.name !== localizableTextToString(config.prompt, $languageConfigStore);
  $: {
    if (!hasEditedFieldName || config.name.length === 0) {
      config.name = localizableTextToString(config.prompt, $languageConfigStore);
    }
  }
</script>

<div class="flex flex-col gap-1">
  {#if config.name}
    <EditableText
      bind:value={config.name}
      on:startedEditing={() => {
        hasEditedFieldName = true;
      }}
    >
      {#if config.is_required}
        <span class="text-red-700">*</span>
      {/if}
      {config.name}
    </EditableText>
  {/if}
  <LocalizableTextInput
    placeholder={exampleContent.prompt}
    bind:value={config.prompt}
    maxCharacters={TELEGRAM_MAX_MESSAGE_LENGTH_CHARS}
  />
  <Toggle bind:checked={config.is_required} size="small">Обязательное</Toggle>
</div>
