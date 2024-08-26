<script lang="ts">
  import { Textarea } from "flowbite-svelte";
  import InputWrapper from "./InputWrapper.svelte";

  export let value: string;
  export let label: string | null = null;
  export let required: boolean = true;
  export let placeholder: string | null = null;
  export let description: string | null = null;
  export let error: string | boolean | null = null;
  export let rows: number = 2;
  export let maxLength: number | null = null;
  export let preventExceedingMaxLength: boolean = false;

  $: {
    if (maxLength !== null && value.length > maxLength && preventExceedingMaxLength) {
      value = value.slice(0, maxLength);
    }
  }
</script>

<InputWrapper {label} {description} {error} {required}>
  <Textarea {rows} {placeholder} {required} bind:value />
  {#if maxLength !== null && value.length / maxLength > 0.5}
    <span class="text-xs {value.length > maxLength ? 'text-red-600' : 'text-gray-500'}">
      {value.length} / {maxLength} символов
      {#if value.length > maxLength && !preventExceedingMaxLength}
        – сообщение может быть разрезано
      {/if}
    </span>
  {/if}
</InputWrapper>
