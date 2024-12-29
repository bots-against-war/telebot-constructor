<script lang="ts">
  import { Button, Heading } from "flowbite-svelte";
  import { PlusOutline } from "flowbite-svelte-icons";
  import { type BotInfo } from "../api/types";
  import Navbar from "../components/Navbar.svelte";
  import Page from "../components/Page.svelte";
  import PageContent from "../components/PageContent.svelte";
  import Timestamp from "../components/Timestamp.svelte";
  import { dashboardPath } from "../routeUtils";
  import { getModalOpener } from "../utils";
  import CreateBotModal from "./CreateBotModal.svelte";

  export let botInfos: BotInfo[];

  const botInfoTimestamp = (bi: BotInfo) => bi.last_events[0]?.timestamp || 0;
  botInfos.sort((b1, b2) => botInfoTimestamp(b2) - botInfoTimestamp(b1));

  const open = getModalOpener();
  if (botInfos.length === 0) {
    open(CreateBotModal);
  }
</script>

<Page>
  <Navbar />
  <PageContent>
    <div class="flex flex-row justify-between items-center mb-4">
      <Heading tag="h3">Мои боты</Heading>
      <Button outline on:click={() => open(CreateBotModal)}>
        <PlusOutline class="w-3 h-3 me-2" />
        Создать
      </Button>
    </div>
    {#each botInfos as botInfo (botInfo.bot_id)}
      <div class="border-primary-300 border-b last:border-none px-3 py-4 hover:bg-primary-100">
        <a href={dashboardPath(botInfo.bot_id)} class="flex flex-row justify-between">
          <span class="font-bold text-xl">{botInfo.display_name}</span>
          <div class="text-gray-500">
            {#if botInfo.last_versions.length > 0}
              <span>v{botInfo.last_versions[botInfo.last_versions.length - 1].version + 1}</span>
              ·
            {/if}
            <Timestamp timestamp={botInfoTimestamp(botInfo)} />
          </div>
        </a>
      </div>
    {/each}
  </PageContent>
</Page>
