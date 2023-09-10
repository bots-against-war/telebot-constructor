<script lang="ts">
  import { Svelvet } from "svelvet";
  import CommandEntryPointNode from "./nodes/CommandEntryPoint/Node.svelte";
  import type { UserFlowConfig } from "../api/types";
  import MessageBlockNode from "./nodes/MessageBlock/Node.svelte";
  import type { SvelvetPosition } from "../types";
  import { mean } from "../utils";

  // TODO: fetch from API based on path/props
  const userFlowConfig: UserFlowConfig = {
    entrypoints: [
      {
        command: {
          entrypoint_id: "command-1",
          command: "start",
          next_block_id: "message-1",
        },
      },
    ],
    blocks: [
      {
        message: {
          block_id: "message-1",
          message_text: "hello world",
          next_block_id: "message-2",
        },
      },
      {
        message: {
          block_id: "message-2",
          message_text: `how are you today?`,
          next_block_id: null,
        },
      },
    ],
    node_display_coords: {
      "command-1": { x: 0, y: 0 },
      "message-1": { x: 100, y: 100 },
      "message-2": { x: 50, y: 250 },
    },
  };

  const nodeDisplayCoords = Object.values(userFlowConfig.node_display_coords);
  const initialCenterPosition: SvelvetPosition = {
    x: mean(nodeDisplayCoords.map((pos) => pos.x)),
    y: mean(nodeDisplayCoords.map((pos) => pos.y)),
  };
</script>

<div class="svelvet-container">
  <button on:click={() => console.log(userFlowConfig)}>DEBUG CONFIG BINDING</button>
  <Svelvet id="my-canvas" TD controls translation={initialCenterPosition}>
    {#each userFlowConfig.entrypoints as entrypoint, idx}
      {#if entrypoint.command !== null}
        <CommandEntryPointNode
          bind:config={userFlowConfig.entrypoints[idx].command}
          bind:position={userFlowConfig.node_display_coords[entrypoint.command.entrypoint_id]}
        />
      {/if}
    {/each}
    {#each userFlowConfig.blocks as block, idx}
      {#if block.message !== null}
        <MessageBlockNode
          bind:config={userFlowConfig.blocks[idx].message}
          bind:position={userFlowConfig.node_display_coords[block.message.block_id]}
        />
      {/if}
    {/each}
  </Svelvet>
</div>

<style>
  .svelvet-container {
    width: 100%;
    height: 100vh;
  }
</style>
