<script lang="ts">
  import { startBot, stopBot } from "../api/lifecycle";
  import { deleteBotConfig } from "../api/botConfig";
  import { reloadConfigs } from "./Dashboard.svelte";
  import { createEventDispatcher } from "svelte";

  // region props
  export let botName: string;
  // endregion
  let botStatus: string;
  const dispatch = createEventDispatcher();

  function updateSelectedBot(selectedBot: string) {
    dispatch("updateSelectedBot", selectedBot);
  }
  async function startBotWithName(name: string) {
    const resp = await startBot(name);
    if (resp.ok) {
      botStatus = "Started";
    } else {
      // @ts-expect-error
      botStatus = `Failed to start: ${resp.error}`;
    }
  }

  async function stopBotWithName(name: string) {
    const resp = await stopBot(name);
    if (resp.ok) {
      botStatus = "Stopped";
    } else {
      // @ts-expect-error
      botStatus = `Failed to stop: ${resp.error}`;
    }
  }

  async function removeBotConfig(name: string) {
    const resp = await deleteBotConfig(name);
    if (!resp.ok) {
      // @ts-expect-error
      botStatus = `Failed to delete: ${resp.error}`;
      return;
    }
    await reloadConfigs();
    updateSelectedBot("");
  }
</script>

<div class="bot-lifecycle">
  <h3>{botName}</h3>
  <button on:click={() => startBotWithName(botName)}>Start</button>
  <button on:click={() => stopBotWithName(botName)}>Stop</button>
  <button on:click={() => removeBotConfig(botName)}>Delete</button>
  <p><span class="text-status">{botStatus || ""}</span></p>
</div>

<style>
  .bot-lifecycle {
    margin: auto;
    text-align: center;
  }
</style>
