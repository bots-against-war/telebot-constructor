<script lang="ts">
  import { onDestroy } from "svelte";
  import ErrorBadge from "../../components/AlertBadge.svelte";
  import type { LocalizableText } from "../../types";
  import { languageConfigStore } from "../stores";
  import LanguageMenu from "./LanguageMenu.svelte";
  import truncate from "@svackages/truncate";

  export let text: LocalizableText;
  export let maxHeightPx: number;

  let selectedLang = $languageConfigStore === null ? null : $languageConfigStore.defaultLanguageCode;

  const unsubscribe = languageConfigStore.subscribe((newLangConfig) => {
    if (
      newLangConfig !== null &&
      selectedLang !== null &&
      !newLangConfig.supportedLanguageCodes.includes(selectedLang)
    ) {
      selectedLang = newLangConfig.defaultLanguageCode;
    }
  });
  onDestroy(unsubscribe);
</script>

{#if $languageConfigStore === null && typeof text === "string"}
  {#key text}
    <div class="max-h-[{maxHeightPx}px]" use:truncate>
      <p>{text}</p>
    </div>
  {/key}
{:else if $languageConfigStore !== null && typeof text === "object"}
  <div class="flex flex-row items-start justify-between gap-1">
    {#key [text, selectedLang]}
      <div class="max-h-[{maxHeightPx}px]" use:truncate>
        <p>{text[selectedLang || ""] || ""}</p>
      </div>
    {/key}
    <LanguageMenu bind:selectedLang />
  </div>
{:else}
  <ErrorBadge text="Internal error: invalid text and lang config combination" />
{/if}
