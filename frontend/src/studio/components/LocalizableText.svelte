<script lang="ts">
  import { Text, Group, Menu, type TextProps } from "@svelteuidev/core";
  import type { LocalizableText } from "../../types";
  import { languageConfigStore } from "../stores";
  import Language from "../../components/Language.svelte";

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
    <Menu override={{ padding: "0.1em" }} position="right" placement="center" gutter={15} withArrow>
      {#each $languageConfigStore.supportedLanguageCodes as language}
        <Menu.Item on:click={() => (selectedLang = language)}>
          <Language {language} tooltip={false} />
        </Menu.Item>
      {/each}
    </Menu>
  </Group>
{/if}
