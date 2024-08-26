<script lang="ts">
  import { Alert, Button, Heading, Li, List } from "flowbite-svelte";
  import { createEventDispatcher } from "svelte";
  import { deleteBotConfig } from "../api/botConfig";
  import { getBotUser } from "../api/botUser";
  import { startBot, stopBot } from "../api/lifecycle";
  import type { BotInfo } from "../api/types";
  import BotUserBadge from "../components/BotUserBadge.svelte";
  import ErrorBadge from "../components/ErrorBadge.svelte";
  import Navbar from "../components/Navbar.svelte";
  import Page from "../components/Page.svelte";
  import PageContent from "../components/PageContent.svelte";
  import Timestamp from "../components/Timestamp.svelte";
  import BreadcrumbHome from "../components/breadcrumbs/BreadcrumbHome.svelte";
  import Breadcrumbs from "../components/breadcrumbs/Breadcrumbs.svelte";
  import DataBadge from "../components/internal/DataBadge.svelte";
  import DataBadgeLoader from "../components/internal/DataBadgeLoader.svelte";
  import { formResultsPagePath, studioPath } from "../routeUtils";
  import { withConfirmation } from "../utils";

  export let botId: string;
  export let botInfo: BotInfo;

  let lastVersion = botInfo.last_versions[botInfo.last_versions.length - 1].version;

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

  const botUserPromise = getBotUser(botId);
</script>

<Page>
  <Navbar />
  <PageContent>
    <Breadcrumbs><BreadcrumbHome /></Breadcrumbs>
    <Heading tag="h2">{botInfo.display_name}</Heading>
    {#if error !== null}
      <Alert color="red">{error}</Alert>
    {/if}
    <div class="mt-5 pt-3 border-t">
      <h2 class="text-xl font-bold">Аккаунт</h2>
      <div class="max-w-[350px]">
        <DataBadge>
          {#await botUserPromise}
            <DataBadgeLoader />
          {:then botUserResult}
            {#if botUserResult.ok}
              <BotUserBadge botUser={botUserResult.data} />
            {:else}
              <ErrorBadge title="Ошибка загрузки данных о боте" text={botUserResult.error} />
            {/if}
          {/await}
        </DataBadge>
      </div>
    </div>
    {#if botInfo.forms_with_responses.length > 0}
      <div class="mt-5 pt-3 border-t">
        <h2 class="text-xl font-bold">Ответы на формы</h2>
        <List>
          {#each botInfo.forms_with_responses as formInfo}
            <Li>
              <div class=" inline-flex flex-row gap-2 items-baseline">
                <span>
                  {#if formInfo.title}
                    {formInfo.title}
                  {:else}
                    "{formInfo.prompt}"
                  {/if}
                </span>
                <Button size="xs" outline href={formResultsPagePath(botId, formInfo.form_block_id)}>Ответы</Button>
              </div>
            </Li>
          {/each}
        </List>
      </div>
    {/if}
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
              <!-- version info -->
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
              <!-- controls -->
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
    </div>
    <div class="mt-5 pt-3 border-t">
      <h2 class="text-xl font-bold">Управление</h2>
      <Button color="red" outline on:click={deleteBotWithConfirmation}>Удалить бота</Button>
    </div>
  </PageContent>
</Page>
