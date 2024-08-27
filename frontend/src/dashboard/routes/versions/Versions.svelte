<script lang="ts">
  import { Button, Heading } from "flowbite-svelte";
  import { ChevronLeftOutline, ChevronRightOutline, RocketSolid } from "flowbite-svelte-icons";
  import { getBotVersionsPage } from "../../../api/botInfo";
  import { startBot, stopBot } from "../../../api/lifecycle";
  import type { BotVersionInfo, BotVersionsPage } from "../../../api/types";
  import ActionIcon from "../../../components/ActionIcon.svelte";
  import BotVersionInfoBadge from "../../../components/BotVersionInfoBadge.svelte";
  import BreadcrumbDashboard from "../../../components/breadcrumbs/BreadcrumbDashboard.svelte";
  import BreadcrumbHome from "../../../components/breadcrumbs/BreadcrumbHome.svelte";
  import Breadcrumbs from "../../../components/breadcrumbs/Breadcrumbs.svelte";
  import ConfirmationModal from "../../../components/ConfirmationModal.svelte";
  import Navbar from "../../../components/Navbar.svelte";
  import Page from "../../../components/Page.svelte";
  import PageContent from "../../../components/PageContent.svelte";
  import { studioPath } from "../../../routeUtils";
  import { getError, getModalOpener } from "../../../utils";

  export let page: BotVersionsPage;
  export let offset: number;
  export let count: number;

  // TODO: package this into a generic pager element!
  // START OF PAGER LOGIC
  let botInfo = page.bot_info;
  let versions = page.versions;
  let totalVersions = page.total_versions;

  let firstIdx: number;
  let lastIdx: number;
  let isStart: boolean;
  let isEnd: boolean;
  $: {
    firstIdx = offset;
    lastIdx = offset + versions.length - 1;
    isStart = firstIdx === 0;
    isEnd = lastIdx >= totalVersions - 1;
  }
  async function loadPage(next: boolean) {
    let sign;
    if (next) {
      if (isEnd) return;
      sign = 1;
    } else {
      if (isStart) return;
      sign = -1;
    }
    const newOffset = offset + sign * count;

    const res = await getBotVersionsPage(botInfo.bot_id, newOffset, count);
    if (res.ok) {
      offset = newOffset;
      versions = res.data.versions;
      totalVersions = res.data.total_versions;
      botInfo = res.data.bot_info;
    } else {
      window.alert("Failed to load page: " + getError(res));
    }
  }
  // END OF PAGER LOGIC

  const isRunning = (ver: BotVersionInfo) => ver.version === botInfo.running_version;
  const isLast = (ver: BotVersionInfo) => ver.version === totalVersions - 1;

  const open = getModalOpener();
  const publishBot = (verNo: number) => {
    open(ConfirmationModal, {
      text:
        `Опубликовать v${verNo}` +
        (botInfo.running_version !== null ? ` вместо v${botInfo.running_version}` : "") +
        "?",
      onConfirm: async () => {
        const resp = await startBot(botInfo.bot_id, { version: verNo });
        if (resp.ok) {
          botInfo.running_version = verNo;
        } else {
          alert(`Ошибка при запуске бота: ${resp.error}`);
          botInfo.running_version = null;
        }
      },
      confirmButtonLabel: "Опубликовать",
    });
  };

  const stopPuslishedBot = () => {
    open(ConfirmationModal, {
      text: "Остановить бота? Он перестанет реагировать на команды и отвечать пользователь:ницам!",
      onConfirm: async () => {
        const resp = await stopBot(botInfo.bot_id);
        if (resp.ok) {
          botInfo.running_version = null;
        } else {
          alert(`Ошибка при остановке бота: ${resp.error}`);
        }
      },
      confirmButtonLabel: "Остановить",
    });
  };
</script>

<Page>
  <Navbar />
  <PageContent>
    <Breadcrumbs>
      <BreadcrumbHome />
      <BreadcrumbDashboard {botInfo} />
    </Breadcrumbs>
    <Heading tag="h3">История версий</Heading>

    <!-- TODO: move to a generic pager element -->
    <div class="text-lg pt-4 flex flex-row gap-5">
      <span>
        <strong>{totalVersions - lastIdx} - {totalVersions - firstIdx}</strong>
        из
        <strong>{totalVersions}</strong>
      </span>
      <div>
        <ActionIcon icon={ChevronLeftOutline} disabled={isStart} on:click={() => loadPage(false)} />
        <ActionIcon icon={ChevronRightOutline} disabled={isEnd} on:click={() => loadPage(true)} />
      </div>
    </div>

    <ol class="relative border-s border-gray-200 mt-2">
      {#each versions.toReversed() as ver (ver.version)}
        <li class="mb-2 ms-3 p-2">
          {#if isRunning(ver)}
            <div class="absolute w-8 h-8 mt-1 -start-4 text-green-600">
              <RocketSolid class="w-8 h-8" />
            </div>
          {:else}
            <div class="absolute w-3 h-3 bg-gray-300 rounded-full mt-2.5 -start-1.5 border border-white" />
          {/if}
          <div class="flex flex-row gap-4 items-center justify-between">
            <div class="flex-grow">
              <BotVersionInfoBadge {ver} carded={false} />
            </div>
            <div class="flex flex-row gap-1 items-baseline">
              {#if isRunning(ver)}
                <Button size="xs" outline color="red" on:click={stopPuslishedBot}>Остановить</Button>
              {:else}
                <Button size="xs" outline color="primary" on:click={() => publishBot(ver.version)}>Опубликовать</Button>
              {/if}
              <Button size="xs" outline href={studioPath(botInfo.bot_id, isLast(ver) ? null : ver.version)}>
                {isLast(ver) ? "Редактировать" : "Посмотреть"}
              </Button>
            </div>
          </div>
        </li>
      {/each}
    </ol>
  </PageContent>
</Page>
