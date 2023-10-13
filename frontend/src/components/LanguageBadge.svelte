<script lang="ts">
  import { Tooltip } from "@svelteuidev/core";
  import DataBadge from "./internal/DataBadge.svelte";
  import ErrorBadge from "./ErrorBadge.svelte";
  import { availableLanguagesStore, lookupLanguage } from "../globalStateStores";
  import LanguageDataBadge from "./LanguageDataBadge.svelte";
  import type { Result } from "../utils";
  import type { LanguageData } from "../api/types";

  export let language: string;
  export let fullName: boolean = false;

  let languageLookupResult: Result<LanguageData>;
  $: languageLookupResult = lookupLanguage(language, $availableLanguagesStore);
  let tooltipOpened = false;
</script>

<DataBadge>
  {#if languageLookupResult.ok}
    <Tooltip
      opened={tooltipOpened}
      label={fullName ? languageLookupResult.data.code : languageLookupResult.data.name}
      on:mouseenter={() => (tooltipOpened = true)}
      on:mouseleave={() => (tooltipOpened = false)}
    >
      <LanguageDataBadge languageData={languageLookupResult.data} {fullName} />
    </Tooltip>
  {:else}
    <ErrorBadge text={languageLookupResult.error} />
  {/if}
</DataBadge>
