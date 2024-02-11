<script lang="ts">
  import { Input } from "flowbite-svelte";
  import InputWrapper from "./InputWrapper.svelte";

  export let value: string;
  export let label: string;
  export let required: boolean = true;
  export let placeholder: string = "";
  export let description: string | null = null;
  export let error: string | boolean | null = null;
</script>

<InputWrapper {label} {description} {error}>
  <Input {label} id={label} name={label} {required} {placeholder} bind:value color={error ? "red" : undefined} />
</InputWrapper>
