<script lang="ts">
  import { t } from "svelte-i18n";
  import { Textarea } from "flowbite-svelte";
  import InputWrapper from "./InputWrapper.svelte";
  import MarkdownTextareaInternal from "./MarkdownTextareaInternal.svelte";

  export let value: string;
  export let label: string | null = null;
  export let required: boolean = true;
  export let placeholder: string | null = null;
  export let description: string | null = null;
  export let error: string | boolean | null = null;

  export let rows: number = 2;
  export let maxLength: number | null = null;
  export let preventExceedingMaxLength: boolean = false;
  export let markdown: boolean = false;

  $: {
    if (maxLength !== null && value.length > maxLength && preventExceedingMaxLength) {
      value = value.slice(0, maxLength);
    }
  }
</script>

<InputWrapper {label} {description} {error} {required}>
  {#if markdown}
    <MarkdownTextareaInternal {rows} {placeholder} {required} bind:value />
  {:else}
    <Textarea {rows} {placeholder} {required} bind:value />
  {/if}
  {#if maxLength !== null && value.length / maxLength > 0.5}
    <span class="text-xs {value.length > maxLength ? 'text-red-600' : 'text-gray-500'}">
      {value.length} / {maxLength}
      {$t("components.text_input.symbols")}
      {#if value.length > maxLength && !preventExceedingMaxLength}
        – {$t("components.text_input.message_might_be_split")}
      {/if}
    </span>
  {/if}
</InputWrapper>
