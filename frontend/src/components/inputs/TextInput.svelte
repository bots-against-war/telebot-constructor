<script lang="ts">
  import { Input } from "flowbite-svelte";
  import InputWrapper from "./InputWrapper.svelte";
  import { getLengthError } from "./utils";

  export let value: string;
  export let styleClass: string = "";
  export let label: string | null = null;
  export let required: boolean = true;
  export let placeholder: string | null = null;
  export let description: string | null = null;
  export let error: string | boolean | null = null;
  export let disabled: boolean = false;
  export let maxLength: number | null = null;

  $: localError = maxLength !== null ? getLengthError(maxLength, value.length) : null;
</script>

<InputWrapper {label} {description} error={localError || error} {required}>
  <Input
    class={styleClass}
    {required}
    {placeholder}
    bind:value
    color={localError || error ? "red" : undefined}
    {disabled}
  />
</InputWrapper>
