<script lang="ts">
  import { Heading, P } from "flowbite-svelte";
  import type { FormInfo } from "../../../api/types";

  export let result: { [k: string]: string | number | number };
  export let formInfo: FormInfo;

  let fieldIds = Object.keys(formInfo.field_names);
</script>

<div>
  {#each fieldIds as fieldId}
    <div class="pt-3">
      <Heading tag="h5">{formInfo.field_names[fieldId] || fieldId}</Heading>
      <P>
        {result[fieldId] || ""}
      </P>
    </div>
  {/each}
</div>
