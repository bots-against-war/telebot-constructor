<script context="module" lang="ts">
  import { listBotConfigs } from "../api/botConfig.js";
  import { unwrap } from "../utils.js";
  import { botConfigs } from "../botConfigsStore";

  export async function reloadConfigs() {
    const configsFromBackend = unwrap(await listBotConfigs());
    botConfigs.set(configsFromBackend);
  }
</script>

<script lang="ts">
  import { Route } from "svelte-routing";
  import CreateBotButton from "./CreateBotButton.svelte";
  import ArrayBots from "../components/ArrayBots.svelte";
  // @ts-expect-error
  import Modal from "svelte-simple-modal";
  import type { BotConfig } from "../api/types";
  import BotLifecycle from "./BotLifecycle.svelte";

  let existingConfigs: { [key: string]: BotConfig } = {};
  let selectedBot = "";
  $: selectedBot = selectedBot || Object.keys(existingConfigs)[0];

  function handleUpdateSelectedBot(event: CustomEvent<string>) {
    if (event.detail) {
      selectedBot = event.detail;
    } else {
      selectedBot = "";
    }
  }

  botConfigs.subscribe((value) => {
    existingConfigs = value;
  });
</script>

<Route path="/">
  <div style="display:flex; flex-flow: row; align-items: center;">
    <div class="right">
      <div class="center">
        <Modal><CreateBotButton /></Modal>
      </div>
      <hr />
      <ArrayBots on:updateSelectedBot={handleUpdateSelectedBot} {selectedBot} />
    </div>
    {#if !selectedBot}
      <p class="text">
        Добро пожаловать в B.A.W., современный конструктор чат-ботов, который поможет вашей инициативе стать еще ближе к
        пользователям.
      </p>
    {:else}
      <BotLifecycle on:updateSelectedBot={handleUpdateSelectedBot} botName={selectedBot} />
    {/if}
  </div>
</Route>
<Route path="/command">
  <div class="center, text">
    <p>Команда</p>
  </div>
</Route>
<Route path="/actions">
  <div class="center, text">
    <p>Действия</p>
  </div>
</Route>
<Route path="/security">
  <div class="center, text">
    <p>Безопасность</p>
  </div>
</Route>

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
