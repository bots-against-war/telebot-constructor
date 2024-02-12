<script lang="ts">
  import { Toggle } from "flowbite-svelte";
  import type { BaseFormFieldConfig } from "../../../../api/types";
  import LocalizableTextInput from "../../../components/LocalizableTextInput.svelte";
  import { getRandomContent as getRandomFormExampleContent } from "../content";

  export let config: BaseFormFieldConfig;

  let exampleContent = getRandomFormExampleContent();

  config.name = "name";
</script>

<div class="flex flex-col gap-1">
  <!-- <TextInput label="Поле" placeholder={exampleContent.name} bind:value={config.name} /> -->
  <LocalizableTextInput label="Вопрос" placeholder={exampleContent.prompt} bind:value={config.prompt} />
  <Toggle bind:checked={config.is_required} size="default">Обязательное</Toggle>
</div>
