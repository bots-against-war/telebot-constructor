<script lang="ts">
  import { Select } from "flowbite-svelte";
  import type { FormFieldConfig } from "../../../../api/types";
  import { getBaseFormFieldConfig, getDefaultFormFieldConfig } from "../utils";
  import BaseFormFieldInputs from "./BaseFormFieldInputs.svelte";
  import ExtraInputsSingleSelectField from "./ExtraInputsSingleSelectField.svelte";
  import FormMemberFrame from "./FormMemberFrame.svelte";
  import { languageConfigStore } from "../../../stores";

  export let fieldConfig: FormFieldConfig;
  export let isMovableUp: boolean;
  export let isMovableDown: boolean;

  let availableKeys = [
    { value: "plain_text", name: "Свободный ответ" },
    { value: "single_select", name: "Выбор" },
  ];

  let selectedKey: string;
  const nonNullKey = Object.entries(fieldConfig).find(([_, config]) => Boolean(config));
  if (nonNullKey) selectedKey = nonNullKey[0];
  else window.alert("Internal error! All keys in field config are null!");

  let promptLang: string | null;
  promptLang = $languageConfigStore ? $languageConfigStore.supportedLanguageCodes[0] : null;
  const handlePromptLanguageChanged = (e: CustomEvent<string>) => {
    promptLang = e.detail;
  };
</script>

<FormMemberFrame {isMovableUp} {isMovableDown} isDeletable on:delete on:moveup on:movedown>
  <div class="p-3 border border-gray-300 bg-gray-100 relative w-full flex flex-col gap-3">
    {#if fieldConfig.plain_text}
      <BaseFormFieldInputs bind:config={fieldConfig.plain_text} on:languageChanged={handlePromptLanguageChanged} />
    {:else if fieldConfig.single_select}
      <BaseFormFieldInputs bind:config={fieldConfig.single_select} on:languageChanged={handlePromptLanguageChanged} />
    {/if}
    <Select
      placeholder=""
      items={availableKeys}
      bind:value={selectedKey}
      on:change={() => {
        fieldConfig = getDefaultFormFieldConfig(getBaseFormFieldConfig(fieldConfig), selectedKey);
      }}
    />
    {#if fieldConfig.plain_text}
      <!--  -->
    {:else if fieldConfig.single_select}
      <ExtraInputsSingleSelectField bind:config={fieldConfig.single_select} selectedLang={promptLang} />
    {/if}
  </div>
</FormMemberFrame>
