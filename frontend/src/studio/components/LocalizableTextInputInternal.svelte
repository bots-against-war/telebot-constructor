<script lang="ts">
  import { InputWrapper, Tabs, Textarea } from "@svelteuidev/core";
  import Language from "../../components/Language.svelte";
  import type { LocalizableText } from "../../types";
  import type { LanguageConfig } from "../stores";

  export let label: string;
  export let description: string | undefined = undefined;
  export let value: LocalizableText;
  export let langConfig: LanguageConfig | null; // undefined = take from global writable store

  if (value instanceof Object && langConfig === null) {
    if (value.length) {
      console.debug("value is multilang, lang config is null, selecting the first localization");
      value = Object.values(value)[0];
    } else {
      console.debug("value is empty object, lang config is null, setting text to empty str");
      value = "";
    }
  } else if (langConfig !== null) {
    if (typeof value === "string") {
      console.debug("value is string, setting as localization to first lang, others empty");
      // @ts-expect-error
      value = Object.fromEntries(langConfig.supportedLanguageCodes.map((lang, idx) => [lang, idx == 0 ? value : ""]));
    } else {
      console.debug("checking localization to all supported langs");
      // @ts-expect-error
      const missingSupportedLangs = langConfig.supportedLanguageCodes.filter((lang) => !value[lang]);
      console.debug(missingSupportedLangs);
      const emptyLocalizations = Object.fromEntries(missingSupportedLangs.map((lang) => [lang, ""]));
      value = { ...value, ...emptyLocalizations };
    }
  }

  let activeLanguageTab = 0;
</script>

{#if langConfig === null && typeof value === "string"}
  <Textarea resize="vertical" {label} {description} bind:value />
{:else if langConfig !== null && langConfig.supportedLanguageCodes.length > 0 && typeof value !== "string"}
  <!--
    key block forces svelte to rerender tabs when the languages change,
    see https://github.com/svelteuidev/svelteui/issues/474 
  -->
  <!-- {#key langConfig} -->
  <InputWrapper {label} {description}>
    <Tabs
      active={activeLanguageTab}
      on:change={(
        // @ts-ignore
        e,
      ) => (activeLanguageTab = e.detail.index)}
    >
      {#each langConfig.supportedLanguageCodes as language}
        <Tabs.Tab icon={Language} iconProps={{ language, fullName: true, tooltip: false }}>
          <Textarea aria-label={`localization-${language}`} resize="vertical" bind:value={value[language]} />
        </Tabs.Tab>
      {/each}
    </Tabs>
  </InputWrapper>
  <!-- {/key} -->
{/if}
