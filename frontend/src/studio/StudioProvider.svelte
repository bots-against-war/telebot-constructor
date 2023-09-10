<script lang="ts">
  import { loadBotConfig, saveBotConfig } from "../api/botConfig";
  import type { BotConfig } from "../api/types";
  import { getError, unwrap } from "../utils";
  import Studio from "./Studio.svelte";

  export let botName: string;

  async function getBotConfig(botName: string): Promise<BotConfig> {
    const loadBotConfigResult = await loadBotConfig(botName);
    if (getError(loadBotConfigResult) !== null) {
      const newBotConfig: BotConfig = {
        token_secret_name: "",
        feedback_handler_config: null,
        user_flow_config: {
          entrypoints: [],
          blocks: [],
          node_display_coords: {},
        },
      };
      const res = await saveBotConfig(botName, newBotConfig);
      return unwrap(res);
    } else {
      return unwrap(loadBotConfigResult);
    }
  }

  const getBotConfigPromise = getBotConfig(botName);
</script>

{#await getBotConfigPromise}
  Loading...
{:then botConfig}
  <Studio {botName} {botConfig} />
{:catch e}
  <h1>Error: {e}</h1>
{/await}
