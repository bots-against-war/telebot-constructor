<script lang="ts">
  import { startBot, stopBot } from "../api/lifecycle";
  import { deleteBotConfig } from "../api/botConfig";
  import { createEventDispatcher } from "svelte";
  import { Alert, Center, Flex, Container, Button } from "@svelteuidev/core";
  import type { BotConfig } from "../api/types";
  import NavButton from "../components/NavButton.svelte";

  // region props
  export let botName: string;
  export let botConfig: BotConfig;
  // endregion
  let botStatus: string | null = null;
  const dispatch = createEventDispatcher();

  async function startBotWithName(name: string) {
    const resp = await startBot(name);
    if (resp.ok) {
      botStatus = "Started";
    } else {
      botStatus = `Failed to start: ${resp.error}`;
    }
  }

  async function stopBotWithName(name: string) {
    const resp = await stopBot(name);
    if (resp.ok) {
      botStatus = "Stopped";
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
</script>

<Container>
  <Center>
    <Flex direction="column" gap="xl">
      <h1>{botConfig.display_name}</h1>
      <Flex gap="xl">
        <NavButton href={`/studio/${botName}`}>Редактировать</NavButton>
        <Button on:click={() => startBotWithName(botName)}>Запустить</Button>
        <Button on:click={() => stopBotWithName(botName)}>Остановить</Button>
        <Button on:click={() => removeBotConfig(botName)}>Удалить</Button>
      </Flex>
      {#if botStatus !== null}
        <Alert color="yellow">{botStatus}</Alert>
      {/if}
    </Flex>
  </Center>
</Container>
