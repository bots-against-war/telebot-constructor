<script lang="ts">
  import { t } from "svelte-i18n";
  import type { SingleSelectFormFieldConfig } from "../../../../api/types";
  import SortableListInput from "../../../components/SortableListInput.svelte";
  import { generateOptionId } from "../utils";

  export let config: SingleSelectFormFieldConfig;
  export let selectedLang: string | null = null;
</script>

<div>
  <SortableListInput
    label={$t("studio.form.options")}
    bind:options={config.options}
    optionConstructor={() => {
      return { id: generateOptionId(), label: "" };
    }}
    {selectedLang}
  />
</div>
