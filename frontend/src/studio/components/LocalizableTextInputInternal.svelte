<script lang="ts">
  import { InputWrapper, Tabs, Textarea, TextInput, Group } from "@svelteuidev/core";
  import Language from "../../components/Language.svelte";
  import type { LocalizableText } from "../../types";
  import type { LanguageConfig } from "../stores";
  import LanguageMenu from "./LanguageMenu.svelte";

  export let label: string | undefined = undefined;
  export let description: string | undefined = undefined;
  export let placeholder: string | undefined = undefined;
  export let value: LocalizableText;
  export let langConfig: LanguageConfig | null;
  export let isLongText: boolean = true;
  export let required: boolean = false;

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
      console.debug(`missingSupportedLangs = ${JSON.stringify(missingSupportedLangs)}`);
      const emptyLocalizations = Object.fromEntries(missingSupportedLangs.map((lang) => [lang, ""]));
      value = { ...value, ...emptyLocalizations };
    }
    console.debug(`after validation and type coercion value = ${JSON.stringify(value)}`);
  }

  let activeLanguageTab = 0;
  let selectedLang = langConfig ? langConfig.supportedLanguageCodes[0] : null;
</script>

{#if !langConfig && typeof value === "string"}
  {#if isLongText}
    <Textarea resize="vertical" {required} {label} {description} {placeholder} bind:value />
  {:else}
    <TextInput {required} {label} {description} {placeholder} bind:value />
  {/if}
{:else if langConfig && langConfig.supportedLanguageCodes.length > 0 && typeof value !== "string" && selectedLang}
  <!--
    key block forces svelte to rerender tabs when the languages change,
    see https://github.com/svelteuidev/svelteui/issues/474 
  -->
  <!-- {#key langConfig} -->
  <InputWrapper {required} label={label || ""} {description} {placeholder}>
    {#if isLongText}
      <Tabs
        active={activeLanguageTab}
        on:change={(
          // @ts-ignore
          e,
        ) => (activeLanguageTab = e.detail.index)}
      >
        {#each langConfig.supportedLanguageCodes as language}
          <Tabs.Tab>
            <Language slot="icon" {language} fullName small tooltip={false} />
            <Textarea aria-label={`localization-${language}`} resize="vertical" bind:value={value[language]} />
          </Tabs.Tab>
        {/each}
      </Tabs>
    {:else}
      <Group>
        <TextInput bind:value={value[selectedLang]} />
        <LanguageMenu bind:selectedLang />
      </Group>
    {/if}
  </InputWrapper>
  <!-- {/key} -->
{/if}
