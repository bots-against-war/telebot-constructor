<script lang="ts">
  import { Textarea } from "flowbite-svelte";
  import InputWrapper from "./InputWrapper.svelte";

  export let value: string;
  export let label: string | null = null;
  export let required: boolean = true;
  export let placeholder: string = "";
  export let description: string | null = null;
  export let error: string | boolean | null = null;
  export let maxLength: number | null = null;

  $: {
    if (maxLength && value.length > maxLength) {
      error = `Текст должен быть короче ${maxLength} символов`; // TODO add dynamic error description for '..1 симвОЛ'
    } else {
      error = null;
    }
  }
</script>

<InputWrapper {label} {description} {error} {required}>
  <Textarea id="message" name="message" label="Your message" rows="2" {placeholder} {required} bind:value />
</InputWrapper>
