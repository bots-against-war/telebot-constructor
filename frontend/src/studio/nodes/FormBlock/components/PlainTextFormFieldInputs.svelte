<script lang="ts">
  import { Stack, Divider } from "@svelteuidev/core";
  import BaseFormFieldInputs from "./BaseFormFieldInputs.svelte";
  import type { PlainTextFormFieldConfig } from "../../../../api/types";

  export let config: PlainTextFormFieldConfig;
</script>

<Stack spacing="xs">
  <BaseFormFieldInputs bind:config />
</Stack>
