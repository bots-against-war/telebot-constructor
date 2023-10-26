<script lang="ts">
  import { TextInput, Switch, Stack } from "@svelteuidev/core";
  import LocalizableTextInput from "../../../components/LocalizableTextInput.svelte";
  import type { BaseFormFieldConfig } from "../../../../api/types";
  import { getRandomContent as getRandomFormExampleContent } from "../content";

  export let config: BaseFormFieldConfig;

  let exampleContent = getRandomFormExampleContent();
</script>

<Stack spacing={10}>
  <TextInput label="Поле" placeholder={exampleContent.name} bind:value={config.name} />
  <Switch bind:checked={config.is_required} size="sm" label="Обязательное" />
  <LocalizableTextInput label="Вопрос" placeholder={exampleContent.prompt} bind:value={config.prompt} />
</Stack>
