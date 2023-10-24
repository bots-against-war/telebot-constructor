<script lang="ts">
  import { TextInput, Switch, Group } from "@svelteuidev/core";
  import { slugify } from "transliteration";
  import LocalizableTextInput from "../../../components/LocalizableTextInput.svelte";
  import type { BaseFormFieldConfig } from "../../../../api/types";

  export let config: BaseFormFieldConfig;

  $: {
    config.id = slugify(config.name, { separator: "_" });
  }
</script>

<Group position="apart" gap="xs">
  <TextInput bind:value={config.name} placeholder="Название" override={{ flexGrow: 100 }} />
  <Switch bind:checked={config.isRequired} size="sm" label="Обязательное" />
</Group>
<LocalizableTextInput placeholder="Вопрос" bind:value={config.prompt} />
