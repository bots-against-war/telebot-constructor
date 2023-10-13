<script lang="ts">
  import { setContext } from "svelte";
  import LoadingScreen from "./components/LoadingScreen.svelte";
  import { availableLanguagesStore } from "./globalStateStores";
  import { getAvailableLanguages } from "./api/misc";
  import { err, ok, type Result } from "./utils";
  import FatalError from "./components/FatalError.svelte";

  async function loadGlobalState(): Promise<Result<null>> {
    // available language list
    const LANGUAGE_DATA_BY_CODE_LOCALSTORAGE_KEY = "languageDataByCode";
    // try loading from localStorage
    const storedDump = localStorage.getItem(LANGUAGE_DATA_BY_CODE_LOCALSTORAGE_KEY);
    if (storedDump !== null) {
      availableLanguagesStore.set(JSON.parse(storedDump));
    } else {
      // if nothing in localStorage, load from backend...
      let languageListLoadingPromise = getAvailableLanguages();
      const availableLanguagesResult = await languageListLoadingPromise;
      if (!availableLanguagesResult.ok) {
        return err(availableLanguagesResult.error);
      }
      let loaded = Object.fromEntries(availableLanguagesResult.data.map((ld) => [ld.code, ld]));
      // ... and save for the future
      localStorage.setItem(LANGUAGE_DATA_BY_CODE_LOCALSTORAGE_KEY, JSON.stringify(loaded));
      availableLanguagesStore.set(loaded);
    }
    return ok(null);
  }

  let globalStateLoadedPromise = loadGlobalState();
</script>

{#await globalStateLoadedPromise}
  <LoadingScreen />
{:then res}
  {#if res.ok}
    <div>
      <slot />
    </div>
  {:else}
    <FatalError error={res.error} />
  {/if}
{/await}
