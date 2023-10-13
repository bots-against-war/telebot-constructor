<script lang="ts">
  import { Text, Tooltip } from "@svelteuidev/core";
  import DataBadge from "./internal/DataBadge.svelte";
  import type { LanguageData } from "../api/types";
  import { err, ok, type Result } from "../utils";
  import DataBadgeLoader from "./internal/DataBadgeLoader.svelte";
  import ErrorBadge from "./ErrorBadge.svelte";
  import { availableLanguagesStore } from "../globalStateStores";

  export let language: string;

  async function loadLanguageData(): Promise<Result<LanguageData>> {
    let availableLanguages = $availableLanguagesStore;
    if (!(language in availableLanguages)) {
      return err(`unknown language code ${language}`);
    } else {
      return ok(availableLanguages[language]);
    }
  }

  const languageDataPromise = loadLanguageData();
  let tooltipOpened = false;
</script>

<DataBadge>
  {#await languageDataPromise}
    <DataBadgeLoader />
  {:then languageDataResult}
    {#if languageDataResult.ok}
      <Tooltip
        opened={tooltipOpened}
        label={languageDataResult.data.name}
        on:mouseenter={() => (tooltipOpened = true)}
        on:mouseleave={() => (tooltipOpened = false)}
      >
        <Text>
          {languageDataResult.data.emoji || "🌐"}
          {languageDataResult.data.code}
        </Text>
      </Tooltip>
    {:else}
      <ErrorBadge text={languageDataResult.error} />
    {/if}
  {/await}
</DataBadge>
