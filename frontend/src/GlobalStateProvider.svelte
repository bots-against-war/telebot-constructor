<script lang="ts">
  import LoadingScreen from "./components/LoadingScreen.svelte";

  import { availableLanguagesStore, loggedInUserStore } from "./globalStateStores";
  import { getAvailableLanguages, fetchPrefilledMessages, getLoggedInUser } from "./api/misc";
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
    // TODO: now we always fetch prefilled messages anew, because they're sometimes updated on backend;
    // we need to turn it off after public releas
    if (true || Object.keys(getPrefilledMessages()).length === 0) {
      const res = await fetchPrefilledMessages();
      if (res.ok) {
        console.debug("Loaded prefilled messages, will save to localStorage", res);
        savePrefilledMessages(res.data);
      } else {
        console.error(`Failed to load prefilled messages: ${res.error}`);
      }
    }

    // 3. logged-in user details
    // TODO: this can be bundled with some other request to reduce network latency, but for now that'll do
    const loggedInUser = await getLoggedInUser();
    if (!loggedInUser.ok) return loggedInUser;
    loggedInUserStore.set(loggedInUser.data);

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
