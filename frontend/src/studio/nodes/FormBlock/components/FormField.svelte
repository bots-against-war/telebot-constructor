<script lang="ts">
  import { Stack, Divider } from "@svelteuidev/core";

  import PlainTextFormFieldInputs from "./PlainTextFormFieldInputs.svelte";

  import type { FormFieldConfig } from "../../../../api/types";

  export let fieldConfig: FormFieldConfig;
</script>

<Stack spacing="xs">
  <!-- TODO: switch for field type with config conversion on change -->
  <Divider label="Текстовое поле" labelPosition="left" override={{ margin: 0 }} />
  {#if fieldConfig.plain_text}
    <PlainTextFormFieldInputs bind:config={fieldConfig.plain_text} />
  {/if}
</Stack>
