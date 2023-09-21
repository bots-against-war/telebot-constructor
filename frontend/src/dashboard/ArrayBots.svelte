<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import type { BotConfigList } from "../types";

  // region props
  export let botConfigs: BotConfigList;
  export let selectedBot: string | null;
  // endregion

  const dispatch = createEventDispatcher();

  function updateSelectedBot(selectedBot: string) {
    dispatch("updateSelectedBot", selectedBot);
  }
</script>

<div class="bots">
  {#each Object.entries(botConfigs) as [configName, config], i}
    <button
      class="bot"
      aria-label={configName}
      aria-current={selectedBot === configName}
      on:click={() => {
        selectedBot = configName;
        updateSelectedBot(configName);
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
