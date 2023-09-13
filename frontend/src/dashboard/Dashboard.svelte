<script lang="ts">
  import { Route } from "svelte-routing";
  import CreateBotButton from "./CreateBotButton.svelte";
  import ArrayBots from "../components/ArrayBots.svelte";
  // @ts-expect-error
  import Modal from "svelte-simple-modal";
  import type { BotConfig } from "../api/types";
  import { botConfigs } from "../botConfigsStore";
  let existingConfigs: { [key: string]: BotConfig } = {};

  let selectedBot = "";

  botConfigs.subscribe((value) => {
    existingConfigs = value;
  });
</script>

<Route path="/">
  <div style="display:flex; flex-flow: row; align-items: center;">
    <div class="right">
      <div class="center">
        <Modal {selectedBot}><CreateBotButton {selectedBot} /></Modal>
      </div>
      <hr />
      <ArrayBots {selectedBot} />
    </div>
    {#if !selectedBot}
      <p class="text">
        Добро пожаловать в B.A.W., современный конструктор чат-ботов, который поможет вашей инициативе стать еще ближе к
        пользователям.
      </p>
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
