<script lang="ts">
  import type { SingleSelectFormFieldConfig } from "../../../../api/types";
  import SortableListInput from "../../../components/SortableListInput.svelte";

  export let config: SingleSelectFormFieldConfig;
</script>

<div>
  <SortableListInput
    label="Варианты"
    bind:options={config.options}
    optionConstructor={() => {
      return { id: `opt-${crypto.randomUUID()}`, label: "" };
    }}
  />
</div>
