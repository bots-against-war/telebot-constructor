<script lang="ts">
  import { Textarea } from "flowbite-svelte";
  import InputWrapper from "./InputWrapper.svelte";

  export let value: string;
  export let label: string | null = null;
  export let required: boolean = true;
  export let placeholder: string | null = null;
  export let description: string | null = null;
  export let error: string | boolean | null = null;
  export let maxLength: number | null = null;
</script>

<InputWrapper {label} {description} {error} {required}>
  <Textarea rows="2" {placeholder} {required} bind:value />
  {#if maxLength !== null}
    <span class="text-xs {value.length > maxLength ? 'text-red-600' : 'text-gray-500'}">
      {value.length} / {maxLength} символов {#if value.length > maxLength}
        (будет разрезано на несколько сообщений)
      {/if}
    </span>
  {/if}
</InputWrapper>
