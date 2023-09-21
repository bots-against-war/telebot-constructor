<script lang="ts">
  import { startBot, stopBot } from "../api/lifecycle";
  import { deleteBotConfig } from "../api/botConfig";
  import { createEventDispatcher } from "svelte";
  import { Alert } from "@svelteuidev/core";

  // region props
  export let botName: string;
  // endregion
  let botStatus: string | null = null;
  const dispatch = createEventDispatcher();

  async function startBotWithName(name: string) {
    const resp = await startBot(name);
    if (resp.ok) {
      botStatus = "Started";
    } else {
      botStatus = `Failed to start: ${resp.error}`;
    }
  }

  async function stopBotWithName(name: string) {
    const resp = await stopBot(name);
    if (resp.ok) {
      botStatus = "Stopped";
    } else {
      botStatus = `Failed to stop: ${resp.error}`;
    }
  }

  async function removeBotConfig(name: string) {
    const resp = await deleteBotConfig(name);
    if (resp.ok) {
      dispatch("botDeleted");
    } else {
      botStatus = `Failed to delete: ${resp.error}`;
    }
  }
</script>

<div class="bot-lifecycle">
  <h3>{botName}</h3>
  <button on:click={() => startBotWithName(botName)}>Start</button>
  <button on:click={() => stopBotWithName(botName)}>Stop</button>
  <button on:click={() => removeBotConfig(botName)}>Delete</button>
  {#if botStatus !== null}
    <Alert color="yellow">{botStatus}</Alert>
  {/if}
</div>

<style>
  .bot-lifecycle {
    margin: auto;
    text-align: center;
  }
</style>
