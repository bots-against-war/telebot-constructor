<script lang="ts">
  import { Input } from "flowbite-svelte";
  import InputWrapper from "./InputWrapper.svelte";
  import * as utils from "./utils";

  export let value: string;
  export let styleClass: string = "";
  export let label: string | null = null;
  export let required: boolean = true;
  export let placeholder: string = "";
  export let description: string | null = null;
  export let error: string | boolean | null = null;
  export let disabled: boolean = false;
  export let maxLength: number | null = null;
  let name: string = utils.defineName(label);

  $: localError = utils.getLengthError(maxLength, value.length);
</script>

<InputWrapper {label} {description} error={localError || error} {required}>
  <Input class={styleClass} {name} {required} {placeholder} bind:value color={error ? "red" : undefined} {disabled} />
</InputWrapper>
