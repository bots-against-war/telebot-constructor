<script lang="ts">
  import { Select } from "flowbite-svelte";
  import { CloseOutline } from "flowbite-svelte-icons";
  import { createEventDispatcher } from "svelte";
  import type { FormFieldConfig } from "../../../../api/types";
  import ActionIcon from "../../../../components/ActionIcon.svelte";
  import { getBaseFormFieldConfig, getDefaultFormFieldConfig } from "../utils";
  import BaseFormFieldInputs from "./BaseFormFieldInputs.svelte";
  import ExtraInputsPlainTextField from "./ExtraInputsPlainTextField.svelte";
  import ExtraInputsSingleSelectField from "./ExtraInputsSingleSelectField.svelte";

  const dispatch = createEventDispatcher<{ delete: null }>();

  export let fieldConfig: FormFieldConfig;

  let availableKeys = [
    { value: "plain_text", name: "Свободный ответ" },
    { value: "single_select", name: "Выбор" },
  ];

  let selectedKey: string;
  const nonNullKey = Object.entries(fieldConfig).find(([_, config]) => Boolean(config));
  if (nonNullKey) selectedKey = nonNullKey[0];
  else window.alert("Internal error! All keys in field config are null!");
</script>

<div class="p-3 border border-gray-300 bg-gray-100 rounded-md relative">
  <div class="delete-button-container">
    <ActionIcon icon={CloseOutline} on:click={() => dispatch("delete")} />
  </div>
  <div class="flex flex-col gap-3">
    {#if fieldConfig.plain_text}
      <BaseFormFieldInputs bind:config={fieldConfig.plain_text} />
    {:else if fieldConfig.single_select}
      <BaseFormFieldInputs bind:config={fieldConfig.single_select} />
    {/if}
    <Select
      items={availableKeys}
      bind:value={selectedKey}
      on:change={() => {
        fieldConfig = getDefaultFormFieldConfig(getBaseFormFieldConfig(fieldConfig), selectedKey);
      }}
    />
    {#if fieldConfig.plain_text}
      <ExtraInputsPlainTextField bind:config={fieldConfig.plain_text} />
    {:else if fieldConfig.single_select}
      <ExtraInputsSingleSelectField bind:config={fieldConfig.single_select} />
    {/if}
  </div>
</div>

<style>
  div.delete-button-container {
    position: absolute;
    right: 5px;
    top: 5px;
    z-index: 1000;
  }
</style>
