<script lang="ts">
  import ArrayBots from "./ArrayBots.svelte";
  import BotLifecycle from "./BotLifecycle.svelte";
  import { Button, Container, Divider, Stack, Text } from "@svelteuidev/core";
  import { type BotInfoList } from "../types";
  import CreateBotModal from "./CreateBotModal.svelte";

  import { PlusOutline } from "flowbite-svelte-icons";

  import { getModalOpener } from "../utils";
  import { type BotInfo } from "../api/types";

  const open = getModalOpener();

  export let botInfos: BotInfoList;

  let selectedBot: string | null = null;
  let selectedBotHash = window.location.hash.slice(1); // slice removes # symbol from the start
  if (selectedBotHash !== null && selectedBotHash in botInfos) {
    selectedBot = selectedBotHash;
  } else if (Object.keys(botInfos).length > 0) {
    selectedBot = Object.keys(botInfos)[0];
  }

  const showNewBotModal = () =>
    open(CreateBotModal, {
      newBotCallback: (name: string, info: BotInfo) => {
        botInfos[name] = info;
        selectedBot = name;
      },
    });
</script>

<div style="display:flex; flex-flow: row; align-items: center;">
  <div class="right">
    <Stack align="center" spacing={5}>
      <Button on:click={showNewBotModal}>
        <PlusOutline slot="leftIcon" width={15} />
        Создать
      </Button>
      <Divider override={{ borderColor: "#0776a0", width: "100%" }} />
      <ArrayBots
        on:updateSelectedBot={(e) => {
          selectedBot = e.detail || null;
        }}
        {botInfos}
        {selectedBot}
      />
    </Stack>
  </div>
  {#if selectedBot === null}
    <Container>
      <Text override={{ fontSize: 30, textAlign: "center" }}>
        Добро пожаловать в B.A.W., современный конструктор чат-ботов, который поможет вашей инициативе стать еще ближе к
        пользователям
      </Text>
    </Container>
  {:else}
    <BotLifecycle
      botName={selectedBot}
      bind:botInfo={botInfos[selectedBot]}
      on:botDeleted={() => {
        if (selectedBot === null) return;
        let updatedBotInfos = { ...botInfos };
        delete updatedBotInfos[selectedBot];
        botInfos = updatedBotInfos;
        selectedBot = null;
      }}
    />
  {/if}
</div>

<style>
  .right {
    /* TODO: better side panel styling with less or no hard-coded pixels */
    width: 200px;
    padding: 10px;
    padding-top: 20px;
    min-height: calc(100vh - 60px - 60px);
    border-radius: 0 20px 20px 0;
    margin-top: 30px;
    margin-bottom: 30px;
    background: linear-gradient(180deg, #85d0ee 0%, rgba(133, 208, 238, 0.6) 100%);
  }
</style>
