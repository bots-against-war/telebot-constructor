<script lang="ts">
  import { createEventDispatcher } from "svelte";

  import { Button, Stack } from "@svelteuidev/core";

  import { type BotInfoList } from "../types";

  // region props
  export let botInfos: BotInfoList;
  export let selectedBot: string | null;
  // endregion

  const dispatch = createEventDispatcher<{ updateSelectedBot: string }>();

  function updateSelectedBot(selectedBot: string) {
    dispatch("updateSelectedBot", selectedBot);
  }
</script>

<Stack align="center" justify="flex-start" spacing="sm">
  {#each Object.entries(botInfos) as [botName, botInfo] (botName)}
    <Button
      variant={selectedBot === botName ? "filled" : "outline"}
      on:click={() => {
        selectedBot = botName;
        updateSelectedBot(botName);
      }}
      override={{ height: "auto", padding: "8px 18px" }}
    >
      {botInfo.display_name}
    </Button>
  {/each}
</Stack>
