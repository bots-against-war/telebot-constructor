<script lang="ts">
  import { Text, Group, type TextProps } from "@svelteuidev/core";
  import type { LocalizableText } from "../../types";
  import { languageConfigStore } from "../stores";
  import LanguageMenu from "./LanguageMenu.svelte";
  import ErrorBadge from "../../components/ErrorBadge.svelte";
  import { onDestroy } from "svelte";

  export let text: LocalizableText;

  interface LocalizableTextProps extends TextProps {
    text: LocalizableText;
  }
  type $$Props = LocalizableTextProps;

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
  <Text>{text}</Text>
{:else if $languageConfigStore !== null && typeof text === "object"}
  <Group noWrap spacing="sm" position="apart" align="start">
    <Text>{text[selectedLang || ""] || ""}</Text>
    <LanguageMenu bind:selectedLang />
  </Group>
{:else}
  <ErrorBadge text="Internal error: invalid text and lang config combination" />
{/if}
