<script lang="ts">
  import ArrayBots from "./ArrayBots.svelte";
  import BotLifecycle from "./BotLifecycle.svelte";
  import type { BotConfigList } from "../types";
  import { Button, Container, Space } from "@svelteuidev/core";
  import CreateBotModal from "./CreateBotModal.svelte";
  import { getModalOpener } from "../utils";
  import type { BotConfig } from "../api/types";
  const open = getModalOpener();

  export let botConfigs: BotConfigList;

  let selectedBot: string | null = null;
  let selectedBotHash = window.location.hash.slice(1); // slice removes # symbol from the start
  if (selectedBotHash !== null && selectedBotHash in botConfigs) {
    selectedBot = selectedBotHash;
  } else if (Object.keys(botConfigs).length > 0) {
    selectedBot = Object.keys(botConfigs)[0];
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
    <Space h="s" />
    <Container>
      <Button on:click={showNewBotModal}>Добавить</Button>
    </Container>
    <hr />
    <ArrayBots
      on:updateSelectedBot={(e) => {
        selectedBot = e.detail || null;
      }}
      {botConfigs}
      {selectedBot}
    />
  </div>
  {#if selectedBot === null}
    <p class="lifecycle-placeholder">
      Добро пожаловать в B.A.W., современный конструктор чат-ботов, который поможет вашей инициативе стать еще ближе к
      пользователям.
    </p>
  {:else}
    <BotLifecycle
      botName={selectedBot}
      botConfig={botConfigs[selectedBot]}
      on:botDeleted={() => {
        if (selectedBot === null) return;
        // @ts-ignore
        let newBotConfigs = { ...botConfigs };
        delete newBotConfigs[selectedBot];
        botConfigs = newBotConfigs;
        selectedBot = null;
      }}
    />
  {/if}
</div>

<style>
  .right {
    /* float: left; */
    width: 332px;
    min-height: 700px;
    /* flex-shrink: 0; */
    border-radius: 0 40px 40px 0;
    background: linear-gradient(180deg, #85d0ee 0%, rgba(133, 208, 238, 0.6) 100%);
    margin-top: calc(144px - 88px);
    margin-bottom: 30px;
    display: flex;
    flex-direction: column;
  }
  hr {
    width: 240px;
    height: 2px;
    background: #0776a0;
  }
  p.lifecycle-placeholder {
    width: 781px;
    height: 147px;
    flex-shrink: 0;
    text-align: center;
    margin: auto;
    font-size: 32px;
  }
</style>
