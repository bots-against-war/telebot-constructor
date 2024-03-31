<script lang="ts">
  import { Alert, Badge, Button, Toggle } from "flowbite-svelte";
  import { Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell } from "flowbite-svelte";
  import { createEventDispatcher } from "svelte";
  import { deleteBotConfig } from "../api/botConfig";
  import { startBot, stopBot } from "../api/lifecycle";
  import type { BotInfo } from "../api/types";
  import { withConfirmation } from "../utils";
  import Timestamp from "../components/Timestamp.svelte";
  import { getBotUser } from "../api/botUser";
  import DataBadge from "../components/internal/DataBadge.svelte";
  import DataBadgeLoader from "../components/internal/DataBadgeLoader.svelte";
  import BotUserBadge from "../components/BotUserBadge.svelte";
  import ErrorBadge from "../components/ErrorBadge.svelte";

  export let botName: string;
  export let botInfo: BotInfo;

  let lastVersion = botInfo.last_versions[botInfo.last_versions.length - 1].version;

  let error: string | null = null;
  const dispatch = createEventDispatcher<{ botDeleted: null }>();

  let isLoading = false;

  async function publishOrStop(version: number) {
    isLoading = true;
    if (version !== botInfo.running_version) {
      const resp = await startBot(botName, { version });
      isLoading = false;
      if (resp.ok) {
        botInfo.running_version = version;
      } else {
        error = `Ошибка при запуске бота: ${resp.error}`;
        botInfo.running_version = null;
      }
    } else {
      const resp = await stopBot(botName);
      isLoading = false;
      if (resp.ok) {
        botInfo.running_version = null;
      } else {
        error = `Ошибка при остановке бота: ${resp.error}`;
      }
    }
  }

  async function deleteBot() {
    const resp = await deleteBotConfig(botName);
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

  const botUserPromise = getBotUser(botName);
</script>

<div class="flex flex-col mx-40 my-10">
  <h1 class="text-3xl font-bold">{botInfo.display_name}</h1>

  {#if error !== null}
    <Alert color="red">{error}</Alert>
  {/if}
  <div class="mt-5 pt-3 border-t">
    <h2 class="text-lg font-bold">Аккаунт</h2>
    <div class=" max-w-[300px]">
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
  <div class="mt-5 pt-3 border-t">
    <h2 class="text-lg font-bold">Версии</h2>
    <ol class="relative border-s border-gray-200 mt-2">
      {#each botInfo.last_versions.toReversed() as verInfo}
        <li
          class={"mb-2 ms-3 p-2 rounded-md border-2 " +
            (verInfo.version === botInfo.running_version
              ? "bg-blue-100 border-blue-300 border-2"
              : "border-transparent")}
        >
          <div class="absolute w-3 h-3 bg-gray-300 rounded-full mt-1.5 -start-1.5 border border-white" />

          <div class="flex flex-row gap-4 items-center justify-between">
            <!-- version info -->
            <div class="flex flex-col">
              <div class="flex flex-row gap-2 items-baseline">
                <span class="font-bold text-lg">v{verInfo.version + 1}</span>
                {#if verInfo.metadata.timestamp}
                  <Timestamp timestamp={verInfo.metadata.timestamp} timeClass="text-gray-500" />
                {/if}
              </div>
              {#if verInfo.metadata.message}
                <span>
                  {verInfo.metadata.message}
                </span>
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
                href={`/studio/${encodeURIComponent(botName)}?version=${encodeURIComponent(verInfo.version)}&saveable=${lastVersion === verInfo.version}`}
              >
                {lastVersion === verInfo.version ? "Редактировать" : "Посмотреть"}
              </Button>
            </div>
          </div>
        </li>
      {/each}
    </ol>
  </div>
  <div class="mt-5 pt-3 border-t">
    <h2 class="text-lg font-bold">Управление</h2>
    <Button color="red" outline on:click={deleteBotWithConfirmation}>Удалить бота</Button>
  </div>
</div>
