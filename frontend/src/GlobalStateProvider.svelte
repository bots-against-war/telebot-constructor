<script lang="ts">
  import LoadingScreen from "./components/LoadingScreen.svelte";
  import { availableLanguagesStore } from "./globalStateStores";
  import { getAvailableLanguages, fetchPrefilledMessages } from "./api/misc";
  import { err, ok, type Result } from "./utils";
  import FatalError from "./components/FatalError.svelte";
  import { getPrefilledMessages, savePrefilledMessages } from "./studio/nodes/FormBlock/prefill";

  async function loadGlobalState(): Promise<Result<null>> {
    // 1. available language list
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

    // 2. prefilled messages
    if (Object.keys(getPrefilledMessages()).length === 0) {
      const res = await fetchPrefilledMessages();
      if (res.ok) {
        console.log("Loaded prefilled messages, will save to localStorage");
        console.log(res);
        savePrefilledMessages(res.data);
      } else {
        console.error(`Failed to load prefilled messages: ${res.error}`);
      }
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
