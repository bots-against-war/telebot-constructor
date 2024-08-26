<script lang="ts">
  import { Input } from "flowbite-svelte";
  import InputWrapper from "./InputWrapper.svelte";

  export let value: string;
  export let styleClass: string = "";
  export let label: string | null = null;
  export let required: boolean = true;
  export let placeholder: string | null = null;
  export let description: string | null = null;
  export let error: string | boolean | null = null;
  export let disabled: boolean = false;
  export let maxLength: number | null = null;

  $: {
    if (maxLength !== null && value.length > maxLength) {
      value = value.slice(0, maxLength);
    }
  }
</script>

<InputWrapper {label} {description} {error} {required}>
  <Input class={styleClass} {required} {placeholder} bind:value color={error ? "red" : undefined} {disabled} />
</InputWrapper>
