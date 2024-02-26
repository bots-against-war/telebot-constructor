<script lang="ts">
  import { Input } from "flowbite-svelte";
  import InputWrapper from "./InputWrapper.svelte";

  export let value: string;
  export let styleClass: string = "";
  export let label: string | undefined = undefined;
  export let required: boolean = true;
  export let placeholder: string = "";
  export let description: string | null = null;
  export let error: string | boolean | null = null;
  export let disabled: boolean = false;
  export let maxLength: number = 0;

  $: {
    if (maxLength !== 0 && value.length > maxLength) {
      error = `Текст должен быть короче ${maxLength} символов`;
    } else {
      error = null;
    }
  }
</script>

<InputWrapper {label} {description} {error} {required}>
  <Input
    {label}
    class={styleClass}
    id={label}
    name={label}
    {required}
    {placeholder}
    bind:value
    color={error ? "red" : undefined}
    {disabled}
  />
</InputWrapper>
