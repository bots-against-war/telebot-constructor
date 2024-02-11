<script lang="ts">
  import { Group, InputWrapper, Tabs, TextInput, Textarea } from "@svelteuidev/core";
  import { ExclamationCircleOutline } from "flowbite-svelte-icons";
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

  const DEBUG_LOG = false;

  function debugLog(msg: string) {
    if (DEBUG_LOG) {
      console.debug(msg);
    }
  }

  debugLog(`before type coercion value = ${JSON.stringify(value)}`);
  if (value instanceof Object && langConfig === null) {
    if (Object.keys(value).length > 0) {
      debugLog("value is multilang, lang config is null, selecting the first localization");
      value = Object.values(value)[0];
    } else {
      debugLog("value is empty object, lang config is null, setting text to empty str");
      value = "";
    }
  } else if (langConfig !== null) {
    if (typeof value === "string") {
      debugLog("value is string, setting as localization to first lang, others empty");
      // @ts-expect-error
      value = Object.fromEntries(langConfig.supportedLanguageCodes.map((lang, idx) => [lang, idx == 0 ? value : ""]));
    } else {
      debugLog("checking localization to all supported langs");
      // @ts-expect-error
      const missingSupportedLangs = langConfig.supportedLanguageCodes.filter((lang) => !value[lang]);
      debugLog(`missingSupportedLangs = ${JSON.stringify(missingSupportedLangs)}`);
      const emptyLocalizations = Object.fromEntries(missingSupportedLangs.map((lang) => [lang, ""]));
      const existingLocalizations = Object.fromEntries(
        // @ts-expect-error
        Object.entries(value).filter(([langCode]) => langConfig.supportedLanguageCodes.includes(langCode)),
      );
      value = { ...existingLocalizations, ...emptyLocalizations };
    }
  }
  debugLog(`after validation and type coercion value = ${JSON.stringify(value)}`);

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
        {#each langConfig.supportedLanguageCodes as language (language)}
          <Tabs.Tab icon={value[language] ? null : ExclamationCircleOutline} iconProps={{ color: "red" }}>
            <Language slot="label" {language} fullName small tooltip={false} />
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
