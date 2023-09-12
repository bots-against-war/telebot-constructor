<script lang="ts">
  import { startBot, stopBot } from "../api/lifecycle";
  import { deleteBotConfig, listBotConfigs } from "../api/botConfig";
  import { unwrap } from "../utils";
  import { onMount } from "svelte";
  import type { BotConfig } from "../api/types";
  import { botConfigs } from "../botConfigsStore";

  let existingConfigs: { [key: string]: BotConfig };
  async function startBotWithName(name: string) {
    const resp = await startBot(name);
    const statusEl = document.getElementById(`${name}-status`);
    // @ts-expect-error
    statusEl.innerHTML = resp.ok ? "Started" : `Failed to start: ${resp.error}`;
  }

  async function stopBotWithName(name: string) {
    const resp = await stopBot(name);
    const statusEl = document.getElementById(`${name}-status`);
    // @ts-expect-error
    statusEl.innerHTML = resp.ok ? "Stopped" : `Failed to stop: ${resp.error}`;
  }

  async function removeBotConfig(name: string) {
    const resp = await deleteBotConfig(name);
    const statusEl = document.getElementById(`${name}-status`);
    // @ts-expect-error
    statusEl.innerHTML = resp.ok ? "" : `Failed to delete: ${resp.error}`;
    await reloadConfigs();
  }

  export async function reloadConfigs() {
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
    <div id="{configName}-status" />
  {/each}
</div>
