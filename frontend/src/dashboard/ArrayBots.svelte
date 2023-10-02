<script lang="ts">
  import { createEventDispatcher } from "svelte";

  import { Button, Stack } from "@svelteuidev/core";

  import type { BotConfigList } from "../types";

  // region props
  export let botConfigs: BotConfigList;
  export let selectedBot: string | null;
  // endregion

  const dispatch = createEventDispatcher();

  function updateSelectedBot(selectedBot: string) {
    dispatch("updateSelectedBot", selectedBot);
  }
</script>

<Stack align="center" justify="flex-start" spacing="sm">
  {#each Object.entries(botConfigs) as [botName, config], i}
    <Button
      variant={selectedBot === botName ? "filled" : "outline"}
      on:click={() => {
        selectedBot = botName;
        updateSelectedBot(botName);
      }}
    >
      {config.display_name}</Button
    >
  {/each}
</Stack>
