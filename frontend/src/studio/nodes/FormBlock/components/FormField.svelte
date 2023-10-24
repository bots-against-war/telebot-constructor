<script lang="ts">
  import { Stack, ActionIcon, NativeSelect } from "@svelteuidev/core";
  import { Trash } from "radix-icons-svelte";

  import BaseFormFieldInputs from "./BaseFormFieldInputs.svelte";

  import type { FormFieldConfig } from "../../../../api/types";
  import { createEventDispatcher } from "svelte";

  const dispatch = createEventDispatcher<{ delete: null }>();

  export let fieldConfig: FormFieldConfig;

  let availableKeys = [
    { value: "plain_text", label: "Свободный" },
    { value: "single_select", label: "Одиночный выбор" },
  ];

  let selectedKey: string;
  const nonNullKey = Object.entries(fieldConfig).find(([_, config]) => Boolean(config));
  if (nonNullKey) selectedKey = nonNullKey[0];
  else window.alert("Internal error! All keys in field config are null!");
</script>

<div class="form-field-container">
  <div class="delete-button-container">
    <ActionIcon on:click={() => dispatch("delete")}>
      <Trash />
    </ActionIcon>
  </div>
  <Stack>
    {#if fieldConfig.plain_text}
      <BaseFormFieldInputs bind:config={fieldConfig.plain_text} />
    {:else if fieldConfig.single_select}
      <BaseFormFieldInputs bind:config={fieldConfig.single_select} />
    {/if}
    <NativeSelect label="Ответ" data={availableKeys} bind:value={selectedKey} />
  </Stack>
</div>

<style>
  div.form-field-container {
    padding: 10px;
    border: 1px rgb(206, 212, 218) solid;
    border-radius: 5px;
    position: relative;
  }
  div.delete-button-container {
    position: absolute;
    right: 5px;
    top: 5px;
  }
</style>
