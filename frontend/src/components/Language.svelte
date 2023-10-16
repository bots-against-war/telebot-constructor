<script lang="ts">
  import { Tooltip } from "@svelteuidev/core";
  import ErrorBadge from "./ErrorBadge.svelte";
  import { availableLanguagesStore, lookupLanguage } from "../globalStateStores";
  import LanguageDataComponent from "./LanguageData.svelte";
  import type { Result } from "../utils";
  import type { LanguageData } from "../api/types";

  export let language: string;
  export let fullName: boolean = false;
  export let tooltip: boolean = true;

  let languageLookupResult: Result<LanguageData>;
  $: languageLookupResult = lookupLanguage(language, $availableLanguagesStore);
  let tooltipOpened = false;
</script>

{#if languageLookupResult.ok}
  <Tooltip
    opened={tooltipOpened}
    label={fullName ? languageLookupResult.data.code : languageLookupResult.data.name}
    on:mouseenter={() => {
      if (tooltip) tooltipOpened = true;
    }}
    on:mouseleave={() => {
      if (tooltip) tooltipOpened = false;
    }}
  >
    <LanguageDataComponent languageData={languageLookupResult.data} {fullName} />
  </Tooltip>
{:else}
  <ErrorBadge text={languageLookupResult.error} />
{/if}
