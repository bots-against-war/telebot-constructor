<script lang="ts">
  import { Textarea } from "flowbite-svelte";
  import InputWrapper from "./InputWrapper.svelte";
  import * as utils from "./utils";

  export let value: string;
  export let label: string | null = null;
  export let required: boolean = true;
  export let placeholder: string = "";
  export let description: string | null = null;
  export let error: string | boolean | null = null;
  export let maxLength: number | null = null;
  let name: string = utils.defineName(label);

  $: localError = utils.getLengthError(maxLength, value.length);
</script>

<InputWrapper {label} {description} error={localError || error} {required}>
  <Textarea {name} rows="2" {placeholder} {required} bind:value />
</InputWrapper>
