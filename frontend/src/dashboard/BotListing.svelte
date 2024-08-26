<script lang="ts">
  import { Button, Heading } from "flowbite-svelte";
  import { PlusSolid } from "flowbite-svelte-icons";
  import { navigate } from "svelte-routing";
  import { type BotInfo } from "../api/types";
  import Footer from "../components/Footer.svelte";
  import Navbar from "../components/Navbar.svelte";
  import Timestamp from "../components/Timestamp.svelte";
  import { dashboardPath } from "../routeUtils";
  import { getModalOpener } from "../utils";
  import CreateBotModal from "./CreateBotModal.svelte";

  const open = getModalOpener();

  export let botInfos: BotInfo[];

  function botInfoTimestamp(bi: BotInfo): number {
    return bi.last_events[0]?.timestamp || 0;
  }

  // TEMP
  botInfos = [
    ...botInfos,
    ...botInfos.map((b) => {
      return { ...b, bot_id: b.bot_id + "1" };
    }),
    ...botInfos.map((b) => {
      return { ...b, bot_id: b.bot_id + "2" };
    }),
  ];

  botInfos.sort((b1, b2) => botInfoTimestamp(b1) - botInfoTimestamp(b2));

  const openNewBotModal = () =>
    open(CreateBotModal, {
      newBotCallback: (botId: string, info: BotInfo) => {
        botInfos.push(info);
        navigate(dashboardPath(botId));
      },
    });
</script>

<div class="min-h-screen flex flex-col">
  <Navbar />
  <main class="flex-grow-[1] flex-shrink-0 w-[900px] mx-auto">
    <div class="pt-8">
      <div class="flex flex-row justify-between items-center">
        <Heading tag="h2">Мои боты</Heading>
        <Button outline on:click={openNewBotModal}>
          <PlusSolid class="w-3 h-3 me-2" />
          Создать
        </Button>
      </div>
      {#each botInfos as botInfo (botInfo.bot_id)}
        <div class="border-gray-400 border-b last:border-none py-2 my-4">
          <a href={dashboardPath(botInfo.bot_id)} class="flex flex-row justify-between">
            <span class="font-bold text-xl">{botInfo.display_name}</span>
            <div>
              <span class="text-gray-500">v{botInfo.last_versions[0].version}</span>
              ·
              <Timestamp timestamp={botInfoTimestamp(botInfo)} timeClass="text-gray-500" />
            </div>
          </a>
        </div>
      {/each}
    </div>
  </main>
  <Footer />
</div>
