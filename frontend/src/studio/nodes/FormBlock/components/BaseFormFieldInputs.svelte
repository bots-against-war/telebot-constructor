<script lang="ts">
  import { TextInput, Switch, Stack } from "@svelteuidev/core";
  import LocalizableTextInput from "../../../components/LocalizableTextInput.svelte";
  import type { BaseFormFieldConfig } from "../../../../api/types";

  export let config: BaseFormFieldConfig;
</script>

<Stack spacing={10}>
  <TextInput label="Поле" placeholder="Любимое животное" bind:value={config.name} />
  <Switch bind:checked={config.is_required} size="sm" label="Обязательное" />
  <LocalizableTextInput label="Вопрос" placeholder="Какое ваше любимое животное?" bind:value={config.prompt} />
</Stack>
