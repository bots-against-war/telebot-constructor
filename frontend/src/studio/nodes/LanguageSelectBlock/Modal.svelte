<script lang="ts">
  import { Stack, InputWrapper } from "@svelteuidev/core";
  import Select from "svelte-select";

  import type { LanguageData, LanguageSelectBlock } from "../../../api/types";

  import NodeModalControls from "../../components/NodeModalControls.svelte";
  import { availableLanguagesStore, lookupLanguage } from "../../../globalStateStores";
  import LanguageDataBadge from "../../../components/LanguageDataBadge.svelte";
  import { unwrap } from "../../../utils";
  import LanguageBadge from "../../../components/LanguageBadge.svelte";

  export let config: LanguageSelectBlock;
  export let onConfigUpdate: (newConfig: LanguageSelectBlock) => any;

  function updateConfig() {
    if (!(supportedLanguageDataList && defaultLanguage)) return;
    config.supported_languages = supportedLanguageDataList.map((ld) => ld.code);
    config.default_language = defaultLanguage.code;
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

  let supportedLanguageDataList: LanguageData[] | undefined = config.supported_languages.map((code) =>
    unwrap(lookupLanguage(code, $availableLanguagesStore)),
  );
  let defaultLanguage: LanguageData | null = config.default_language
    ? unwrap(lookupLanguage(config.default_language, $availableLanguagesStore))
    : null;

  let isConfigValid: boolean;
  $: isConfigValid = Boolean(supportedLanguageDataList && defaultLanguage !== null);

  function ensureDefaultLanguageIsSupported() {
    if (
      supportedLanguageDataList &&
      (defaultLanguage === null || !supportedLanguageDataList.includes(defaultLanguage))
    ) {
      defaultLanguage = supportedLanguageDataList[0];
    }
  }
  ensureDefaultLanguageIsSupported();
</script>

<div>
  <h3>Выбор языка</h3>
  <Stack>
    <InputWrapper
      label="Поддерживаемые языки"
      description="Начните вводить код или название языка по-английски"
      override={{ width: "100%" }}
    >
      <Select
        itemId="code"
        placeholder=""
        bind:value={supportedLanguageDataList}
        loadOptions={loadMatchingLanguages}
        on:change={ensureDefaultLanguageIsSupported}
        on:clear={ensureDefaultLanguageIsSupported}
        multiple
      >
        <div slot="item" let:item class="select-internal-container">
          <LanguageDataBadge languageData={item} fullName />
        </div>
        <div slot="selection" let:selection class="select-internal-container">
          <LanguageDataBadge languageData={selection} />
        </div>
      </Select>
    </InputWrapper>

    {#if supportedLanguageDataList}
      <InputWrapper
        label="Язык по умолчанию"
        description="Будет использоваться, если не подходит язык интерфейса Telegram"
        override={{ width: "100%" }}
      >
        <Select itemId="code" placeholder="" bind:value={defaultLanguage} items={supportedLanguageDataList || []}>
          <div slot="item" let:item class="select-internal-container">
            <LanguageDataBadge languageData={item} fullName />
          </div>
          <div slot="selection" let:selection class="select-internal-container">
            <LanguageDataBadge languageData={selection} fullName />
          </div>
        </Select>
      </InputWrapper>
    {/if}
  </Stack>
  <NodeModalControls saveable={isConfigValid} on:save={updateConfig} />
</div>

<style>
  div.select-internal-container {
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
</style>
