<script lang="ts">
  import ArrayBots from "./ArrayBots.svelte";
  import BotLifecycle from "./BotLifecycle.svelte";
  import type { BotConfigList } from "../types";
  import { Button } from "@svelteuidev/core";
  import CreateBotModal from "./CreateBotModal.svelte";
  import { getModalOpener } from "../utils";
  import type { BotConfig } from "../api/types";
  const open = getModalOpener();

  export let botConfigs: BotConfigList;

  let selectedBot = Object.keys(botConfigs).length > 0 ? Object.keys(botConfigs)[0] : null;

  function handleUpdateSelectedBot(event: CustomEvent<string>) {
    if (event.detail) {
      selectedBot = event.detail;
    } else {
      selectedBot = "";
    }
  }

  const showNewBotModal = () =>
    open(CreateBotModal, {
      newBotCallback: (name: string, config: BotConfig) => {
        botConfigs[name] = config;
      },
    });
</script>

<div style="display:flex; flex-flow: row; align-items: center;">
  <div class="right">
    <div class="center">
      <div style="margin: auto;">
        <p><Button radius={40} on:click={showNewBotModal}>Новый бот</Button></p>
      </div>
    </div>
    <hr />
    <ArrayBots on:updateSelectedBot={handleUpdateSelectedBot} {botConfigs} {selectedBot} />
  </div>
  {#if selectedBot === null}
    <p class="text">
      Добро пожаловать в B.A.W., современный конструктор чат-ботов, который поможет вашей инициативе стать еще ближе к
      пользователям.
    </p>
  {:else}
    <BotLifecycle on:updateSelectedBot={handleUpdateSelectedBot} botName={selectedBot} />
  {/if}
</div>

<style>
  .right {
    float: left;
    width: 332px;
    min-height: 700px;
    flex-shrink: 0;
    border-radius: 0 40px 40px 0;
    background: linear-gradient(180deg, #85d0ee 0%, rgba(133, 208, 238, 0.6) 100%);
    margin-top: calc(144px - 88px);
    margin-bottom: 30px;
  }
  hr {
    width: 240px;
    height: 2px;
    background: #0776a0;
  }
</style>
