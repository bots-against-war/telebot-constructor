<script lang="ts">
  import { loadBotConfig } from "../api/botConfig";
  import type { BotConfig } from "../api/types";
  import FatalError from "../components/FatalError.svelte";
  import LoadingScreen from "../components/LoadingScreen.svelte";
  import { unwrap } from "../utils";
  import Studio from "./Studio.svelte";

  export let botName: string;

  async function getBotConfig(botName: string): Promise<BotConfig> {
    const loadBotConfigResult = await loadBotConfig(botName);
    return unwrap(loadBotConfigResult);
  }

  const getBotConfigPromise = getBotConfig(botName);
</script>

{#await getBotConfigPromise}
  <LoadingScreen />
{:then botConfig}
  <Studio {botName} {botConfig} />
{:catch error}
  <FatalError {error} />
{/await}
