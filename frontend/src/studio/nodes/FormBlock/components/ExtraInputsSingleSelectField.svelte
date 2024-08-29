<script lang="ts">
  import type { SingleSelectFormFieldConfig } from "../../../../api/types";
  import SortableListInput from "../../../components/SortableListInput.svelte";
  import { generateOptionId } from "../utils";

  export let config: SingleSelectFormFieldConfig;
</script>

<div>
  <SortableListInput
    label="Варианты"
    bind:options={config.options}
    optionConstructor={() => {
      return { id: generateOptionId(), label: "" };
    }}
  />
</div>
