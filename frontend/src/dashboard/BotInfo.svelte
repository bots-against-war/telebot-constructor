<script lang="ts">
  import { Alert, Button, Heading } from "flowbite-svelte";
  import { ArrowRightOutline, RocketSolid } from "flowbite-svelte-icons";
  import { createEventDispatcher } from "svelte";
  import { deleteBotConfig } from "../api/botConfig";
  import { updateBotDisplayName } from "../api/botInfo";
  import { startBot, stopBot } from "../api/lifecycle";
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
  import { formResultsPagePath, studioPath, versionsPagePath } from "../routeUtils";
  import { withConfirmation } from "../utils";
  import BotInfoCard from "./BotInfoCard.svelte";
  import BotEventList from "./components/BotEventList.svelte";

  export let botId: string;
  export let botInfo: BotInfo;

  let lastVersionInfo = botInfo.last_versions[botInfo.last_versions.length - 1];
  let runningVersionInfo: BotVersionInfo | null = null;
  const matches = botInfo.last_versions.filter((vi) => vi.version === botInfo.running_version);
  if (matches.length > 0) {
    runningVersionInfo = matches[0];
  }

  let editedDisplayName = botInfo.display_name;

  let error: string | null = null;
  const dispatch = createEventDispatcher<{ botDeleted: null }>();

  let isLoading = false;

  async function publishOrStop(version: number) {
    isLoading = true;
    if (version !== botInfo.running_version) {
      // optimistically update events, this should be mostly accurate
      if (botInfo.running_version !== null) {
        botInfo.last_events.push({ event: "stopped", timestamp: new Date().getTime() / 1000, username: "" });
      }
      const resp = await startBot(botId, { version });
      // optimistically update events, this should be mostly accurate
      botInfo.last_events.push({
        event: "started",
        timestamp: new Date().getTime() / 1000,
        username: "",
        version: version,
      });
      isLoading = false;
      if (resp.ok) {
        botInfo.running_version = version;
      } else {
        error = `Ошибка при запуске бота: ${resp.error}`;
        botInfo.running_version = null;
      }
    } else {
      const resp = await stopBot(botId);
      botInfo.last_events.push({ event: "stopped", timestamp: new Date().getTime() / 1000, username: "" });
      isLoading = false;
      if (resp.ok) {
        botInfo.running_version = null;
      } else {
        error = `Ошибка при остановке бота: ${resp.error}`;
      }
    }
  }

  async function deleteBot() {
    const resp = await deleteBotConfig(botId);
    if (resp.ok) {
      dispatch("botDeleted");
    } else {
      error = `Failed to delete: ${resp.error}`;
    }
  }

  const deleteBotWithConfirmation = withConfirmation(
    "Вы уверены, что хотите удалить бота? Это действие дельзя отменить.",
    () => deleteBot(),
    "Удалить",
  );
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
        Конструктор
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
                Работает
              {:else}
                <RocketSolid class="w-5 h-5" />
                Остановлен
              {/if}
            </div>
          </div>
          {#if runningVersionInfo !== null}
            <div class="flex flex-col gap-1 mb-1">
              <span>Запущена версия:</span>
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

        <BotInfoCard title="Управление" moreLinkTitle="Перейти" moreLinkHref="/TBD-settings"></BotInfoCard>
      </div>
      <div class="flex-1 flex flex-col gap-4">
        <BotInfoCard title="Статистика">
          <strong class="text-2xl">🚧👷🏗️🚧</strong>
          <span>В разработке</span>
        </BotInfoCard>

        <BotInfoCard title="Активность" moreLinkTitle="Вся активность" moreLinkHref="/TBD-settings">
          <BotEventList events={botInfo.last_events} />
        </BotInfoCard>

        <BotInfoCard title="Ошибки бота">
          <strong class="text-2xl">🚧👷🏗️🚧</strong>
          <span>В разработке</span>
        </BotInfoCard>
      </div>
    </div>
    <!-- 
    
    <div class="mt-5 pt-3 border-t">
      <h2 class="text-xl font-bold">Версии</h2>
      <ol class="relative border-s border-gray-200 mt-2">
        {#each botInfo.last_versions.toReversed() as verInfo (verInfo.version)}
          <li
            class={"mb-2 ms-2 p-2 rounded-md border-2 " +
              (verInfo.version === botInfo.running_version
                ? "bg-blue-100 border-blue-300 border-2"
                : "border-transparent")}
          >
            <div class="absolute w-3 h-3 bg-gray-300 rounded-full mt-2.5 -start-1.5 border border-white" />
            <div class="flex flex-row gap-4 items-center justify-between">
              <div class="flex flex-row gap-1 items-baseline">
                <span>v{verInfo.version + 1}</span>
                {#if verInfo.metadata.message}
                  <span class="font-bold">
                    {verInfo.metadata.message}
                  </span>
                {/if}
                {#if verInfo.metadata.timestamp}
                  · <Timestamp timestamp={verInfo.metadata.timestamp} timeClass="text-gray-500" />
                {/if}
              </div>
              <div>
                <Button size="xs" disabled={isLoading} outline on:click={() => publishOrStop(verInfo.version)}>
                  {botInfo.running_version === verInfo.version ? "Остановить" : "Опубликовать"}
                </Button>
                <Button
                  size="xs"
                  outline
                  href={studioPath(botId, verInfo.version === lastVersion ? null : verInfo.version)}
                >
                  {lastVersion === verInfo.version ? "Редактировать" : "Посмотреть"}
                </Button>
              </div>
            </div>
          </li>
        {/each}
      </ol>
      <div class="text-gray-400">TBD: полный список версий</div>
    </div>
    <div class="mt-5 pt-3 border-t">
      <h2 class="text-xl font-bold">Активность</h2>
      <ol class="relative border-s border-gray-200 mt-2">
        {#each botInfo.last_events.toReversed() as event (event.timestamp)}
          <li class="mb-1 ms-2 p-1">
            <div class="absolute w-2 h-2 bg-gray-300 rounded-full mt-1.5 -start-1 border border-white" />
            <div class="flex flex-row gap-2 items-baseline">
              {#if event.event}
                <span>
                  {#if event.event === "started"}
                    опубликована {typeof event.version === "number" ? `v${event.version + 1}` : "версия-заглушка"}
                  {:else if event.event === "edited"}
                    создана v{event.new_version + 1}
                  {:else if event.event === "stopped"}
                    бот остановлен
                  {/if}
                </span>
              {/if}
              {#if event.timestamp}
                · <Timestamp timestamp={event.timestamp} timeClass="text-gray-500" />
              {/if}
            </div>
          </li>
        {/each}
      </ol>
      <div class="text-gray-400">TBD: полный лог активности</div>
    </div> -->
  </PageContent>
</Page>
