<script lang="ts">
  import { startBot, stopBot } from "../api/lifecycle";
  import { deleteBotConfig } from "../api/botConfig";
  import { createEventDispatcher } from "svelte";
  import { Alert, Center, Flex, Container, Button, Badge, Text, Input } from "@svelteuidev/core";
  import type { BotInfo } from "../api/types";
  import NavButton from "../components/NavButton.svelte";
  import { withConfirmation } from "../utils";

  // region props
  export let botName: string;
  export let botInfo: BotInfo;
  // endregion

  let botStatus: string | null = null;
  const dispatch = createEventDispatcher<{ botDeleted: null }>();

  let dateTimeFormat = Intl.DateTimeFormat("en-GB", {
    dateStyle: "short",
    timeStyle: "short",
    timeZone: botInfo.timezone ? botInfo.timezone : "UTC",
  });

  async function startBotWithName(name: string) {
    const resp = await startBot(name);
    if (resp.ok) {
      botStatus = "Started";
      botInfo.is_running = true;
    } else {
      botStatus = `Failed to start: ${resp.error}`;
    }
  }

  async function stopBotWithName(name: string) {
    const resp = await stopBot(name);
    if (resp.ok) {
      botStatus = "Stopped";
      botInfo.is_running = false;
    } else {
      botStatus = `Failed to stop: ${resp.error}`;
    }
  }

  async function removeBotConfig(name: string) {
    const resp = await deleteBotConfig(name);
    if (resp.ok) {
      dispatch("botDeleted");
    } else {
      botStatus = `Failed to delete: ${resp.error}`;
    }
  }

  const deleteBotWithConfirmation = withConfirmation(
    "Вы уверены, что хотите удалить бота? Это действие дельзя отменить.",
    () => removeBotConfig(botName),
    "Удалить",
  );

  const h1TextStyle = {
    "font-size": "34px",
    "font-weight": "bold",
  };
</script>

<Container>
  <Center>
    <Flex direction="column" gap="xl">
      <Input
        override={h1TextStyle}
        variant="unstyled"
        size="xl"
        rightSectionWidth={120}
        bind:value={botInfo.display_name}
      >
        <Badge slot="rightSection" color="green">{botInfo.is_running ? "Запущен" : "Остановлен"}</Badge>
      </Input>

      <Text size="lg" color="gray">
        {#if botInfo.created_at}
          Дата создания: {dateTimeFormat.format(new Date(botInfo.created_at))}
        {/if}
        {#if botInfo.updated_at}
          <br />
          Дата последнего редактирования: {dateTimeFormat.format(new Date(botInfo.updated_at))}
        {/if}
        {#if botInfo.last_run_at}
          <br />
          Дата последнего запуска: {dateTimeFormat.format(new Date(botInfo.last_run_at))}
        {/if}
      </Text>
      <Flex gap="xl">
        <NavButton href={`/studio/${botName}`}>Редактировать</NavButton>
        <Button on:click={() => startBotWithName(botName)}>Запустить</Button>
        <Button on:click={() => stopBotWithName(botName)}>Остановить</Button>
        <Button color="red" on:click={deleteBotWithConfirmation}>Удалить</Button>
      </Flex>
      {#if botStatus !== null}
        <Alert color="yellow">{botStatus}</Alert>
      {/if}
    </Flex>
  </Center>
</Container>
