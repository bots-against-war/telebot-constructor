<script lang="ts">
  import { loadBotConfig } from "../api/botConfig";
  import type { BotConfig } from "../api/types";
  import FatalError from "../components/FatalError.svelte";
  import LoadingScreen from "../components/LoadingScreen.svelte";
  import { unwrap } from "../utils";
  import Studio from "./Studio.svelte";

  export let botId: string;

  const urlParams = new URLSearchParams(window.location.search);

  const versionString = urlParams.get("version");
  let version = versionString ? parseInt(versionString) : null;
  // convert NaN -> null
  version = typeof version === "number" && isNaN(version) ? null : version;

  const urlReadonly = urlParams.get("readonly");
  const readonly = urlReadonly === "true" ? true : urlReadonly === "false" ? false : version !== null; // by default, set readonly for non-last versions

  console.debug(`Loading studio for bot id, version, readonly:`, botId, version, readonly);

  async function getBotConfig(botId: string): Promise<BotConfig> {
    const loadBotConfigResult = await loadBotConfig(botId, version);
    return unwrap(loadBotConfigResult);
  }

  const getBotConfigPromise = getBotConfig(botId);
</script>

{#await getBotConfigPromise}
  <LoadingScreen />
{:then botConfig}
  <Studio {botId} {botConfig} {readonly} />
{:catch error}
  <FatalError {error} />
{/await}
