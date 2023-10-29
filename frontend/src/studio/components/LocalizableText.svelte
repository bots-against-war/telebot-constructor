<script lang="ts">
  import { Text, Group, Menu, type TextProps } from "@svelteuidev/core";
  import type { LocalizableText } from "../../types";
  import { languageConfigStore } from "../stores";
  import Language from "../../components/Language.svelte";
  import LanguageMenu from "./LanguageMenu.svelte";

  export let text: LocalizableText;

  interface LocalizableTextProps extends TextProps {
    text: LocalizableText;
  }
  type $$Props = LocalizableTextProps;

  let selectedLang = $languageConfigStore === null ? null : $languageConfigStore.defaultLanguageCode;
</script>

{#if $languageConfigStore === null && typeof text === "string"}
  <Text>{text}</Text>
{:else if $languageConfigStore !== null && typeof text === "object"}
  <Group noWrap spacing="sm" position="apart" align="start">
    <Text>{text[selectedLang || ""] || ""}</Text>
    <LanguageMenu bind:selectedLang />
  </Group>
{/if}
