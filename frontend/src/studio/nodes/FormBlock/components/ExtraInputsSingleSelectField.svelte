<script lang="ts">
  import { Stack } from "@svelteuidev/core";
  import type { SingleSelectFormFieldConfig } from "../../../../api/types";
  import SortableListInput from "../../../components/SortableListInput.svelte";

  export let config: SingleSelectFormFieldConfig;
</script>

<Stack>
  <SortableListInput
    label="Варианты"
    bind:options={config.options}
    optionConstructor={() => {
      return { id: `opt-${crypto.randomUUID()}`, label: "" };
    }}
  />
</Stack>
