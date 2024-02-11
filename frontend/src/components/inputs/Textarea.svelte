<script lang="ts">
  import { Textarea } from "flowbite-svelte";
  import InputWrapper from "./InputWrapper.svelte";

  export let value: string;
  export let label: string | undefined;
  export let required: boolean = true;
  export let placeholder: string = "";
  export let description: string | null = null;
  export let error: string | boolean | null = null;
</script>

<InputWrapper {label} {description} {error} {required}>
  <Textarea id="message" name="message" label="Your message" rows="4" {placeholder} {required} bind:value />
</InputWrapper>
