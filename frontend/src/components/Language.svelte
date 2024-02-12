<script lang="ts">
  import { Tooltip } from "flowbite-svelte";
  import type { LanguageData } from "../api/types";
  import { availableLanguagesStore, lookupLanguage } from "../globalStateStores";
  import type { Result } from "../utils";
  import ErrorBadge from "./ErrorBadge.svelte";
  import LanguageDataComponent from "./LanguageData.svelte";

  export let language: string;
  export let fullName: boolean = false;
  export let tooltip: boolean = true;

  let languageLookupResult: Result<LanguageData>;
  $: languageLookupResult = lookupLanguage(language, $availableLanguagesStore);
</script>

{#if languageLookupResult.ok}
  {#if tooltip}
    <Tooltip triggeredBy={language}>
      {fullName ? languageLookupResult.data.code : languageLookupResult.data.name}
    </Tooltip>
  {/if}
  <div>
    <LanguageDataComponent languageData={languageLookupResult.data} {fullName} />
  </div>
{:else}
  <ErrorBadge text={languageLookupResult.error} />
{/if}
