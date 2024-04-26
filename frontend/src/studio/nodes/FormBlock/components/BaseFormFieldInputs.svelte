<script lang="ts">
  import { Input, Toggle } from "flowbite-svelte";
  import { CheckOutline } from "flowbite-svelte-icons";
  import type { BaseFormFieldConfig } from "../../../../api/types";
  import ActionIcon from "../../../../components/ActionIcon.svelte";
  import LocalizableTextInput from "../../../components/LocalizableTextInput.svelte";
  import { languageConfigStore } from "../../../stores";
  import { localizableTextToString } from "../../../utils";
  import { getRandomContent as getRandomFormExampleContent } from "../content";
  export let config: BaseFormFieldConfig;

  let exampleContent = getRandomFormExampleContent();
  let hasEditedFieldName = config.name !== localizableTextToString(config.prompt, $languageConfigStore);
  let isEditingFieldName = false;
  $: {
    if (!hasEditedFieldName) {
      config.name = localizableTextToString(config.prompt, $languageConfigStore);
    }
  }
</script>

<div class="flex flex-col gap-1">
  {#if config.name}
    {#if isEditingFieldName}
      <div class="flex flex-row gap-3 items-baseline">
        <Input class="font-semibold py-1" placeholder={exampleContent.name} bind:value={config.name} />
        <ActionIcon
          icon={CheckOutline}
          on:click={() => {
            isEditingFieldName = false;
          }}
        />
      </div>
    {:else}
      <button
        class="font-semibold cursor-text hover:underline p-0 border-none m-0 w-full text-left"
        on:click={() => {
          isEditingFieldName = true;
          hasEditedFieldName = true;
        }}
      >
        {#if config.is_required}
          <span class="text-red-700">*</span>
        {/if}
        {config.name}
      </button>
    {/if}
  {/if}
  <LocalizableTextInput placeholder={exampleContent.prompt} bind:value={config.prompt} />
  <Toggle bind:checked={config.is_required} size="small">Обязательное</Toggle>
</div>
