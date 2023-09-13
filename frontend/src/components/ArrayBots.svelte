<script lang="ts">
  import { startBot, stopBot } from "../api/lifecycle";
  import { deleteBotConfig, listBotConfigs } from "../api/botConfig";
  import { unwrap } from "../utils";
  import { onMount } from "svelte";
  import type { BotConfig } from "../api/types";
  import { botConfigs } from "../botConfigsStore";

  let existingConfigs: { [key: string]: BotConfig } = {};
  const botStatuses: { [key: string]: string } = {};

  export let selectedBot: string;
  $: selectedBot = selectedBot || Object.keys(existingConfigs)[0];

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

<!--<div id="container">-->
<!--  {#each Object.entries(existingConfigs) as [configName, config], i}-->
<!--    <h3>{configName}</h3>-->
<!--    <p>-->
<!--      Token secret: <code>{config.token_secret_name}</code>-->
<!--    </p>-->
<!--    <button on:click={() => startBotWithName(configName)}>Start</button>-->
<!--    <button on:click={() => stopBotWithName(configName)}>Stop</button>-->
<!--    <button on:click={() => removeBotConfig(configName)}>Delete</button>-->
<!--    <p><span class="text-status">{botStatuses[configName] || ""}</span></p>-->
<!--  {/each}-->
<!--</div>-->

<div class="bots">
  {#each Object.entries(existingConfigs) as [configName, config], i}
    <button
      class="bot"
      aria-label={configName}
      aria-current={selectedBot === configName}
      on:click={() => {
        selectedBot = configName;
      }}
    >
      {configName}</button
    >
  {/each}
</div>

<style>
  .bots {
    display: flex;
    flex-flow: column;
    align-items: center;
  }

  .bot {
    border-radius: 40px;
    border: 2px solid #62b1d0;
    background: #fff;
    box-shadow:
      0 7px 15px 0 rgba(0, 77, 87, 0.1),
      0 26px 26px 0 rgba(0, 77, 87, 0.09),
      0 59px 36px 0 rgba(0, 77, 87, 0.05),
      0 106px 42px 0 rgba(0, 77, 87, 0.01),
      0 165px 46px 0 rgba(0, 77, 87, 0);
    display: flex;
    width: 240px;
    height: 50px;
    padding: 20px 56px;
    margin: 10px;
    justify-content: center;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
  }

  .bot[aria-current="true"] {
    background: #0776a0;
    box-shadow:
      0 7px 15px 0 rgba(0, 77, 87, 0.1),
      0 26px 26px 0 rgba(0, 77, 87, 0.09),
      0 59px 36px 0 rgba(0, 77, 87, 0.05),
      0 106px 42px 0 rgba(0, 77, 87, 0.01),
      0 165px 46px 0 rgba(0, 77, 87, 0);
  }
</style>
