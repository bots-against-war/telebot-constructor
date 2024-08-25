<script lang="ts">
  import { Button, Listgroup } from "flowbite-svelte";
  import { PlusSolid } from "flowbite-svelte-icons";
  import { type BotInfo } from "../api/types";
  import Footer from "../components/Footer.svelte";
  import Navbar from "../components/Navbar.svelte";
  import { type BotInfoList } from "../types";
  import { getModalOpener } from "../utils";
  import BotInfoScreen from "./BotInfoScreen.svelte";
  import CreateBotModal from "./CreateBotModal.svelte";

  const open = getModalOpener();

  export let botInfos: BotInfoList;

  let selectedBot: string | null = null;
  let selectedBotHash = window.location.hash.slice(1); // slice removes # symbol from the start
  if (selectedBotHash && selectedBotHash in botInfos) {
    selectedBot = selectedBotHash;
  } else if (Object.keys(botInfos).length > 0) {
    selectedBot = Object.keys(botInfos)[0];
  }

  const openNewBotModal = () =>
    open(CreateBotModal, {
      newBotCallback: (name: string, info: BotInfo) => {
        botInfos[name] = info;
        selectedBot = name;
      },
    });

  // this is needed due to incomplete typing in flowbite
  // @ts-ignore
  const getName = (s: string) => s.name;
</script>

<div class="min-h-screen flex flex-col">
  <Navbar />
  <div class="grid grid-cols-sidebar gap-4 flex-grow-[100]">
    <aside class="bg-primary-50 p-5 overflow-y-auto">
      <Button class="w-full mb-3" outline on:click={openNewBotModal}>
        <PlusSolid class="w-3 h-3 me-2" />
        Создать
      </Button>
      {#if Object.keys(botInfos).length > 0}
        <Listgroup
          active
          class="w-auto rounded-none"
          items={Object.entries(botInfos).map(([botId, botInfo]) => {
            return {
              name: botInfo.display_name,
              id: botId,
              current: botId === selectedBot,
            };
          })}
          let:item
          on:click={(e) => (selectedBot = e.detail.id)}
        >
          {getName(item)}
        </Listgroup>
      {/if}
    </aside>
    <div class="min-h-full flex flex-row justify-center align-middle">
      {#if selectedBot === null}
        <div class="flex flex-col justify-center align-middle text-3xl text-gray-300">
          <strong>Telebot constructor</strong>
        </div>
      {:else}
        <BotInfoScreen
          botId={selectedBot}
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
  </div>
  <Footer />
</div>
