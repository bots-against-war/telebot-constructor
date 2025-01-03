<script lang="ts">
  import { t } from "svelte-i18n";
  import Select from "svelte-select";
  import type { LanguageData, LanguageSelectBlock } from "../../../api/types";
  import LanguageDataComponent from "../../../components/LanguageData.svelte";
  import InputWrapper from "../../../components/inputs/InputWrapper.svelte";
  import { TELEGRAM_MAX_MESSAGE_LENGTH_CHARS } from "../../../constants";
  import { availableLanguagesStore, lookupLanguage } from "../../../globalStateStores";
  import { unwrap } from "../../../utils";
  import LocalizableTextInput from "../../components/LocalizableTextInputInternal.svelte";
  import NodeModalBody from "../../components/NodeModalBody.svelte";
  import NodeModalControls from "../../components/NodeModalControls.svelte";
  import { languageConfigStore } from "../../stores";
  import { NODE_TITLE } from "../display";

  export let config: LanguageSelectBlock;
  export let onConfigUpdate: (newConfig: LanguageSelectBlock) => any;

  function updateConfig() {
    if (!(supportedLanguageDataList && defaultLanguage)) return;
    config.supported_languages = supportedLanguageDataList.map((ld) => ld.code);
    config.default_language = defaultLanguage.code;
    config.menu_config.propmt = prompt;
    languageConfigStore.set({
      supportedLanguageCodes: config.supported_languages,
      defaultLanguageCode: config.default_language,
    });
    onConfigUpdate(config);
  }

  async function loadMatchingLanguages(filterText: string) {
    filterText = filterText.trim().toLowerCase();
    if (filterText.length < 2) {
      return [];
    }
    return Object.values($availableLanguagesStore)
      .filter((ld) => {
        // for short filters and "non-standard" languages require precise match
        if (!ld.emoji && filterText.length < 6) {
          return ld.code.toLowerCase() === filterText || ld.name.toLowerCase() === filterText;
        } else {
          return (
            ld.code.toLowerCase().includes(filterText) ||
            ld.name.toLowerCase().includes(filterText) ||
            (ld.local_name && ld.local_name.toLowerCase().includes(filterText)) ||
            (ld.emoji && filterText.includes(ld.emoji))
          );
        }
      })
      .sort((ld1, ld2) => {
        if (ld2.emoji) {
          if (ld1.emoji) return ld1.code.localeCompare(ld2.code);
          else return 1;
        } else {
          if (ld1.emoji) return -1;
          else return ld1.code.localeCompare(ld2.code);
        }
      });
  }

  let supportedLanguageDataList: LanguageData[] = config.supported_languages.map((code) =>
    unwrap(lookupLanguage(code, $availableLanguagesStore)),
  );
  let forceMenuRerenderCounter = 0;
  let defaultLanguage: LanguageData | null | undefined = config.default_language
    ? unwrap(lookupLanguage(config.default_language, $availableLanguagesStore))
    : null;
  let prompt = config.menu_config.propmt;

  let isConfigValid: boolean;
  $: isConfigValid = Boolean(supportedLanguageDataList && defaultLanguage !== null);

  function handleSupportedLanguageListUpdate() {
    if (
      supportedLanguageDataList &&
      (!defaultLanguage || !supportedLanguageDataList.map((ld) => ld.code).includes(defaultLanguage.code))
    ) {
      defaultLanguage = supportedLanguageDataList[0];
    }
    forceMenuRerenderCounter += 1;
  }
</script>

<NodeModalBody title={NODE_TITLE.language_select}>
  {#key forceMenuRerenderCounter}
    {#if supportedLanguageDataList && defaultLanguage}
      <LocalizableTextInput
        label={$t("studio.language_select.message_text_label")}
        description={$t("studio.language_select.message_text_descr")}
        bind:value={prompt}
        langConfig={{
          supportedLanguageCodes: supportedLanguageDataList.map((ld) => ld.code),
          defaultLanguageCode: defaultLanguage.code,
        }}
        maxCharacters={TELEGRAM_MAX_MESSAGE_LENGTH_CHARS}
      />
    {/if}
  {/key}

  <InputWrapper
    label={$t("studio.language_select.supported_langs_label")}
    description={$t("studio.language_select.supported_langs_descr")}
  >
    <Select
      itemId="code"
      placeholder=""
      bind:value={supportedLanguageDataList}
      loadOptions={loadMatchingLanguages}
      on:change={handleSupportedLanguageListUpdate}
      on:clear={handleSupportedLanguageListUpdate}
      multiple
    >
      <div slot="item" let:item class="select-internal-container">
        <LanguageDataComponent languageData={item} fullName />
      </div>
      <div slot="selection" let:selection class="select-internal-container">
        <LanguageDataComponent languageData={selection} />
      </div>
    </Select>
  </InputWrapper>

  {#key forceMenuRerenderCounter}
    <InputWrapper
      label={$t("studio.language_select.default_lang_label")}
      description={$t("studio.language_select.default_lang_descr")}
      required={false}
    >
      <Select itemId="code" placeholder="" bind:value={defaultLanguage} items={supportedLanguageDataList}>
        <div slot="item" let:item class="select-internal-container">
          <LanguageDataComponent languageData={item} fullName />
        </div>
        <div slot="selection" let:selection class="select-internal-container">
          <LanguageDataComponent languageData={selection} fullName />
        </div>
      </Select>
    </InputWrapper>
  {/key}

  <NodeModalControls saveable={isConfigValid} on:save={updateConfig} />
</NodeModalBody>

<style>
  div.select-internal-container {
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
</style>
