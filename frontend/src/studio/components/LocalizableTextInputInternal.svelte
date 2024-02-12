<script lang="ts">
  import { TabItem, Tabs } from "flowbite-svelte";
  import { ExclamationCircleOutline } from "flowbite-svelte-icons";
  import Language from "../../components/Language.svelte";
  import InputWrapper from "../../components/inputs/InputWrapper.svelte";
  import TextInput from "../../components/inputs/TextInput.svelte";
  import Textarea from "../../components/inputs/Textarea.svelte";
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

  const INTERNAL_DEBUG_LOG = false;
  function internalDebug(msg: string) {
    if (INTERNAL_DEBUG_LOG) {
      console.debug(msg);
    }
  }

  internalDebug(`before type coercion value = ${JSON.stringify(value)}`);
  if (value instanceof Object && langConfig === null) {
    if (Object.keys(value).length > 0) {
      internalDebug("value is multilang, lang config is null, selecting the first localization");
      value = Object.values(value)[0];
    } else {
      internalDebug("value is empty object, lang config is null, setting text to empty str");
      value = "";
    }
  } else if (langConfig !== null) {
    if (typeof value === "string") {
      internalDebug("value is string, setting as localization to first lang, others empty");
      // @ts-expect-error
      value = Object.fromEntries(langConfig.supportedLanguageCodes.map((lang, idx) => [lang, idx == 0 ? value : ""]));
    } else {
      internalDebug("checking localization to all supported langs");
      // @ts-expect-error
      const missingSupportedLangs = langConfig.supportedLanguageCodes.filter((lang) => !value[lang]);
      internalDebug(`missingSupportedLangs = ${JSON.stringify(missingSupportedLangs)}`);
      const emptyLocalizations = Object.fromEntries(missingSupportedLangs.map((lang) => [lang, ""]));
      const existingLocalizations = Object.fromEntries(
        // @ts-expect-error
        Object.entries(value).filter(([langCode]) => langConfig.supportedLanguageCodes.includes(langCode)),
      );
      value = { ...existingLocalizations, ...emptyLocalizations };
    }
  }
  internalDebug(`after validation and type coercion value = ${JSON.stringify(value)}`);

  let selectedLang = langConfig ? langConfig.supportedLanguageCodes[0] : null;
</script>

{#if !langConfig && typeof value === "string"}
  {#if isLongText}
    <Textarea {required} {label} {description} {placeholder} bind:value />
  {:else}
    <TextInput {required} {label} {description} {placeholder} bind:value />
  {/if}
{:else if langConfig && langConfig.supportedLanguageCodes.length > 0 && typeof value !== "string" && selectedLang}
  <InputWrapper label={label || ""} {description}>
    {#if isLongText}
      <div>
        <Tabs style="underline" contentClass="mt-1">
          {#each langConfig.supportedLanguageCodes as language, idx (language)}
            <TabItem
              open={idx === 0}
              activeClasses="p-2 text-primary-600 border-b-2 border-primary-600"
              inactiveClasses="p-2 border-b-2 border-transparent hover:text-gray-600 hover:border-gray-300 text-gray-500"
            >
              <div slot="title" class="flex flex-row gap-1 items-center">
                {#if !value[language]}
                  <ExclamationCircleOutline color="red" size="md" />
                {/if}
                <Language {language} fullName tooltip={false} />
              </div>
              <Textarea label={undefined} {placeholder} bind:value={value[language]} />
            </TabItem>
          {/each}
        </Tabs>
      </div>
    {:else}
      <div class="flex flex-row gap-1 items-baseline">
        <TextInput label={undefined} bind:value={value[selectedLang]} />
        <LanguageMenu bind:selectedLang />
      </div>
    {/if}
  </InputWrapper>
{/if}
