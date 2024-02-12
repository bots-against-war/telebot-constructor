<script lang="ts">
  import { onDestroy } from "svelte";
  import ErrorBadge from "../../components/ErrorBadge.svelte";
  import type { LocalizableText } from "../../types";
  import { languageConfigStore } from "../stores";
  import LanguageMenu from "./LanguageMenu.svelte";

  export let text: LocalizableText;

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
  <p>{text}</p>
{:else if $languageConfigStore !== null && typeof text === "object"}
  <div class="flex flex-row items-start justify-between gap-1">
    <p>{text[selectedLang || ""] || ""}</p>
    <LanguageMenu bind:selectedLang />
  </div>
{:else}
  <ErrorBadge text="Internal error: invalid text and lang config combination" />
{/if}
