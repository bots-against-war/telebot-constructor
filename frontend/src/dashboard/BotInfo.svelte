<script lang="ts">
  import { Alert, Button, Heading } from "flowbite-svelte";
  import { ArrowRightOutline, RocketSolid } from "flowbite-svelte-icons";
  import { updateBotDisplayName } from "../api/botInfo";
  import type { BotInfo, BotVersionInfo } from "../api/types";
  import BotUserBadge from "../components/BotUserBadge.svelte";
  import BotVersionInfoBadge from "../components/BotVersionInfoBadge.svelte";
  import GroupChatBadge from "../components/GroupChatBadge.svelte";
  import JumpingIcon from "../components/JumpingIcon.svelte";
  import Navbar from "../components/Navbar.svelte";
  import Page from "../components/Page.svelte";
  import PageContent from "../components/PageContent.svelte";
  import BreadcrumbHome from "../components/breadcrumbs/BreadcrumbHome.svelte";
  import Breadcrumbs from "../components/breadcrumbs/Breadcrumbs.svelte";
  import EditableText from "../components/inputs/EditableText.svelte";
  import { formResultsPagePath, settingsPath, studioPath, versionsPagePath } from "../routeUtils";
  import BotInfoCard from "./BotInfoCard.svelte";
  import BotEventList from "./components/BotEventList.svelte";

  export let botInfo: BotInfo;

  const botId = botInfo.bot_id;

  let lastVersionInfo = botInfo.last_versions[botInfo.last_versions.length - 1];
  let runningVersionInfo: BotVersionInfo | null = null;
  const matches = botInfo.last_versions.filter((vi) => vi.version === botInfo.running_version);
  if (matches.length > 0) {
    runningVersionInfo = matches[0];
  }

  let editedDisplayName = botInfo.display_name;

  let error: string | null = null;
</script>

<Page>
  <Navbar />
  <PageContent>
    <Breadcrumbs><BreadcrumbHome /></Breadcrumbs>
    <div class="flex flex-row justify-between items-start gap-2">
      <EditableText bind:value={editedDisplayName} on:edited={() => updateBotDisplayName(botId, editedDisplayName)}>
        <Heading tag="h3">{editedDisplayName}</Heading>
      </EditableText>
      <Button href={studioPath(botId, null)}>
        <strong>Конструктор</strong>
        <ArrowRightOutline class="w-4 h-4 ml-3" strokeWidth="3" />
      </Button>
    </div>
    <!-- FIXME: better error handling, but'll do for now -->
    {#if error !== null}
      <Alert color="red">{error}</Alert>
    {/if}
    <div class="flex flex-row mt-6 gap-5">
      <div class="flex-1 flex flex-col gap-4">
        <BotInfoCard moreLinkHref={versionsPagePath(botId)} moreLinkTitle="Все версии">
          <div class="flex items-center justify-between pb-3 w-full">
            <span class="text-lg font-bold text-gray-900">Статус</span>
            <div
              class="flex items-center gap-2 px-3 py-2 border {runningVersionInfo !== null
                ? 'text-green-600'
                : 'text-gray-900'}"
            >
              {#if runningVersionInfo !== null}
                <JumpingIcon>
                  <RocketSolid class="w-5 h-5" />
                </JumpingIcon>
                <strong>Работает</strong>
              {:else}
                <RocketSolid class="w-5 h-5" />
                Остановлен
              {/if}
            </div>
          </div>
          {#if runningVersionInfo !== null}
            <div class="flex flex-col gap-1 mb-1">
              <span>Запущена версия</span>
              <BotVersionInfoBadge ver={runningVersionInfo} />
            </div>
          {/if}
          {#if runningVersionInfo === null || runningVersionInfo.version !== lastVersionInfo.version}
            <div class="flex flex-col gap-1 mb-1">
              <span>
                Последняя версия {#if runningVersionInfo !== null}
                  (<strong>+{lastVersionInfo.version - runningVersionInfo.version}</strong>)
                {/if}
              </span>
              <BotVersionInfoBadge ver={lastVersionInfo} />
            </div>
          {/if}
        </BotInfoCard>

        <BotInfoCard title="Аккаунт">
          <BotUserBadge {botId} />
        </BotInfoCard>

        {#if botInfo.admin_chat_ids.length > 0}
          <BotInfoCard title="Рабочие чаты">
            <div class="flex flex-col gap-2">
              {#each botInfo.admin_chat_ids as admin_chat_id}
                <GroupChatBadge {botId} chatId={admin_chat_id} />
              {/each}
            </div>
          </BotInfoCard>
        {/if}

        {#if botInfo.forms_with_responses.length > 0}
          <BotInfoCard title="Ответы на формы">
            {#each botInfo.forms_with_responses as formInfo}
              <div class="border-gray-300 border-l border-b last:border-b-0 px-3 py-4 hover:bg-gray-100">
                <a href={formResultsPagePath(botId, formInfo.form_block_id)} class="flex flex-row justify-between">
                  <span>
                    {#if formInfo.title}
                      {formInfo.title}
                    {:else}
                      "{formInfo.prompt}"
                    {/if}
                  </span>
                  <span class="text-gray-500 text-nowrap">
                    Ответы ({formInfo.total_responses})
                  </span>
                </a>
              </div>
            {/each}
          </BotInfoCard>
        {/if}

        <BotInfoCard title="Управление" moreLinkTitle="Перейти" moreLinkHref={settingsPath(botId)}></BotInfoCard>
      </div>
      <div class="flex-1 flex flex-col gap-4">
        <BotInfoCard title="Статистика">
          <strong class="text-2xl">🚧👷🏗️🚧</strong>
          <span>В разработке</span>
        </BotInfoCard>

        <!-- TODO: full activity page -->
        <!-- <BotInfoCard title="Активность" moreLinkTitle="Вся активность" moreLinkHref="/activity-TBD"> -->
        <BotInfoCard title="Активность">
          <BotEventList events={botInfo.last_events} />
        </BotInfoCard>

        <BotInfoCard title="Ошибки бота">
          <strong class="text-2xl">🚧👷🏗️🚧</strong>
          <span>В разработке</span>
        </BotInfoCard>
      </div>
    </div>
  </PageContent>
</Page>
