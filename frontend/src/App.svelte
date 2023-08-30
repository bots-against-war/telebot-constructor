<script lang="ts">
  import { Node, Svelvet } from "svelvet";
  import CommandEntryPointNode from "./studio/nodes/CommandEntryPointNode.svelte";
  import type { UserFlowConfig } from "./api/types";
  import MessageBlockNode from "./studio/nodes/MessageBlockNode.svelte";

  const exampleConfig: UserFlowConfig = {
    entrypoints: [{ command: { command: "start", next_block_id: "message-1" } }],
    blocks: [
      {
        message: {
          block_id: "message-1",
          message_text: "hello world",
          next_block_id: "message-2",
        },
      },
    ],
  };
</script>

<main>
  <div class="svelvet-container">
    <Svelvet id="my-canvas" TD controls on:connection={(e) => console.log(e)}>
      {#each exampleConfig.entrypoints as entrypoint}
        {#if entrypoint.command !== null}
          <CommandEntryPointNode bind:config={entrypoint.command} />
        {/if}
      {/each}
      {#each exampleConfig.blocks as block}
        {#if block.message !== null}
          <MessageBlockNode bind:config={block.message} />
        {/if}
      {/each}
    </Svelvet>
  </div>
</main>

<style>
  .svelvet-container {
    width: 100%;
    height: 100vh;
  }
</style>
