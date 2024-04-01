<script lang="ts">
  import { loadBotConfig } from "../api/botConfig";
  import type { BotConfig } from "../api/types";
  import FatalError from "../components/FatalError.svelte";
  import LoadingScreen from "../components/LoadingScreen.svelte";
  import { unwrap } from "../utils";
  import Studio from "./Studio.svelte";

  export let botName: string;

  const urlParams = new URLSearchParams(window.location.search);

  const versionString = urlParams.get("version");
  let version = versionString ? parseInt(versionString) : null;
  // convert NaN -> null
  version = typeof version === "number" && isNaN(version) ? null : version;

  const isSaveable = urlParams.get("saveable") === "true";

  console.log(`Loadig studio for bot id = ${botName}, version = ${version}, is saveable = ${isSaveable}`);

  async function getBotConfig(botName: string): Promise<BotConfig> {
    const loadBotConfigResult = await loadBotConfig(botName, version);
    return unwrap(loadBotConfigResult);
  }

  const getBotConfigPromise = getBotConfig(botName);
</script>

{#await getBotConfigPromise}
  <LoadingScreen />
{:then botConfig}
  <Studio {botName} {botConfig} {isSaveable} />
{:catch error}
  <FatalError {error} />
{/await}
