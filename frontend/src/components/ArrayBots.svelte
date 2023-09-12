<script lang="ts">
  import { startBot, stopBot } from "../api/lifecycle";
  import { deleteBotConfig, listBotConfigs } from "../api/botConfig";
  import { unwrap } from "../utils";
  import { onMount } from "svelte";
  import type { BotConfig } from "../api/types";
  import { botConfigs } from "../botConfigsStore";

  let existingConfigs: { [key: string]: BotConfig };
  const botStatuses: { [key: string]: string } = {};

  async function startBotWithName(name: string) {
    const resp = await startBot(name);
    if (resp.ok) {
      botStatuses[name] = "Started";
    } else {
      // @ts-expect-error
      botStatuses[name] = `Failed to start: ${resp.error}`;
    }
  }

  async function stopBotWithName(name: string) {
    const resp = await stopBot(name);
    if (resp.ok) {
      botStatuses[name] = "Stopped";
    } else {
      // @ts-expect-error
      botStatuses[name] = `Failed to stop: ${resp.error}`;
    }
  }

  async function removeBotConfig(name: string) {
    const resp = await deleteBotConfig(name);
    if (!resp.ok) {
      // @ts-expect-error
      botStatuses[name] = `Failed to delete: ${resp.error}`;
      return;
    }
    await reloadConfigs();
  }

  async function reloadConfigs() {
    const configsFromBackend = unwrap(await listBotConfigs());
    botConfigs.set(configsFromBackend);
  }

  onMount(async () => {
    await reloadConfigs();
  });

  botConfigs.subscribe((value) => {
    existingConfigs = value;
  });
</script>

<div id="container">
  {#each Object.entries(existingConfigs) as [configName, config], i}
    <h3>{configName}</h3>
    <p>
      Token secret: <code>{config.token_secret_name}</code>
    </p>
    <button on:click={() => startBotWithName(configName)}>Start</button>
    <button on:click={() => stopBotWithName(configName)}>Stop</button>
    <button on:click={() => removeBotConfig(configName)}>Delete</button>
    <p><span class="text-status">{botStatuses[configName] || ""}</span></p>
  {/each}
</div>
