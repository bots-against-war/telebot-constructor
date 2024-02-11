<script lang="ts">
  import { Alert, Badge, Button, Toggle } from "flowbite-svelte";
  import { Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell } from "flowbite-svelte";
  import { createEventDispatcher } from "svelte";
  import { deleteBotConfig } from "../api/botConfig";
  import { startBot, stopBot } from "../api/lifecycle";
  import type { BotInfo } from "../api/types";
  import { withConfirmation } from "../utils";
  import Timestamp from "../components/Timestamp.svelte";

  // region props
  export let botName: string;
  export let botInfo: BotInfo;
  // endregion

  let botStatus: string | null = null;
  const dispatch = createEventDispatcher<{ botDeleted: null }>();

  let runningStatus: string;
  const updateRunningStatus = () => {
    runningStatus = botInfo.is_running ? "Запущен" : "Остановлен";
  };
  updateRunningStatus();

  async function toggleBotRunning() {
    if (!botInfo.is_running) {
      runningStatus = "Запускаем...";
      const resp = await startBot(botName);
      if (resp.ok) {
        botInfo.is_running = true;
        botInfo.last_run_at = new Date().toISOString();
        updateRunningStatus();
      } else {
        runningStatus = `Ошибка: ${resp.error}`;
      }
    } else {
      runningStatus = "Останавливаем...";
      const resp = await stopBot(botName);
      if (resp.ok) {
        botInfo.is_running = false;
        updateRunningStatus();
      } else {
        runningStatus = `Ошибка: ${resp.error}`;
      }
    }
  }

  async function deleteBot() {
    const resp = await deleteBotConfig(botName);
    if (resp.ok) {
      dispatch("botDeleted");
    } else {
      botStatus = `Failed to delete: ${resp.error}`;
    }
  }

  const deleteBotWithConfirmation = withConfirmation(
    "Вы уверены, что хотите удалить бота? Это действие дельзя отменить.",
    () => deleteBot(),
    "Удалить",
  );
</script>

<div class="flex flex-col mx-20">
  <h1 class="text-3xl font-bold">{botInfo.display_name}</h1>
  <div class=" my-2">
    <Toggle size="large" checked={botInfo.is_running} on:click={toggleBotRunning}>{runningStatus}</Toggle>
  </div>
  <Table class="w-auto">
    <TableBody>
      {#if botInfo.created_at}
        <TableBodyRow>
          <TableBodyCell>Создан</TableBodyCell>
          <TableBodyCell>
            <Timestamp isoString={botInfo.created_at} />
          </TableBodyCell>
        </TableBodyRow>
      {/if}
      {#if botInfo.last_updated_at}
        <TableBodyRow>
          <TableBodyCell>Отредактирован</TableBodyCell>
          <TableBodyCell>
            <Timestamp isoString={botInfo.last_updated_at} />
          </TableBodyCell>
        </TableBodyRow>
      {/if}
      {#if botInfo.last_run_at}
        <TableBodyRow>
          <TableBodyCell>Запущен</TableBodyCell>
          <TableBodyCell>
            <Timestamp isoString={botInfo.last_run_at} />
          </TableBodyCell>
        </TableBodyRow>
      {/if}
    </TableBody>
  </Table>
  <div class=" mt-2">
    <Button href={`/studio/${botName}`}>Редактировать</Button>
    <Button color="red" on:click={deleteBotWithConfirmation}>Удалить</Button>
  </div>
  {#if botStatus !== null}
    <Alert color="red">{botStatus}</Alert>
  {/if}
</div>
