<script lang="ts">
  import { Svelvet } from "svelvet";
  import CommandEntryPointNode from "./nodes/CommandEntryPoint/Node.svelte";
  import type { UserFlowConfig, UserFlowNodePosition } from "../api/types";
  import MessageBlockNode from "./nodes/MessageBlock/Node.svelte";
  import DeletableEdge from "./components/DeletableEdge.svelte";

  // TODO: fetch from API based on path/props
  const userFlowConfig: UserFlowConfig = {
    entrypoints: [
      {
        command: {
          entrypoint_id: "command-start",
          command: "start",
          next_block_id: "message-1",
        },
      },
      {
        command: {
          entrypoint_id: "command-help",
          command: "help",
          next_block_id: "message-2",
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
      "command-start": { x: 150, y: 0 },
      "command-help": { x: 300, y: -10 },
      "message-1": { x: 0, y: 100 },
      "message-2": { x: 150, y: 250 },
    },
  };

  function newUserFlowNodePosition(): UserFlowNodePosition {
    return { x: 0, y: 0 };
  }

  function getOnDeleteEntrypoint(idx: number) {
    return () => {
      userFlowConfig.entrypoints = userFlowConfig.entrypoints.toSpliced(idx, 1);
    };
  }
  function getOnDeleteBlock(idx: number) {
    return () => {
      userFlowConfig.blocks = userFlowConfig.blocks.toSpliced(idx, 1);
    };
  }
</script>

<div class="svelvet-container">
  <Svelvet TD controls fitView edge={DeletableEdge}>
    {#each userFlowConfig.entrypoints as entrypoint, idx}
      {#if entrypoint.command !== null}
        <CommandEntryPointNode
          on:delete={getOnDeleteEntrypoint(idx)}
          bind:config={userFlowConfig.entrypoints[idx].command}
          bind:position={userFlowConfig.node_display_coords[entrypoint.command.entrypoint_id]}
        />
      {/if}
    {/each}
    {#each userFlowConfig.blocks as block, idx}
      {#if block.message !== null}
        <MessageBlockNode
          on:delete={getOnDeleteBlock(idx)}
          bind:config={userFlowConfig.blocks[idx].message}
          bind:position={userFlowConfig.node_display_coords[block.message.block_id]}
        />
      {/if}
    {/each}
  </Svelvet>
  <div class="custom-controls">
    <button
      on:click={() => {
        const newEntrypointId = `entrypoint-command-${userFlowConfig.entrypoints.length}`;
        userFlowConfig.node_display_coords[newEntrypointId] = newUserFlowNodePosition();
        userFlowConfig.entrypoints.push({
          command: {
            entrypoint_id: newEntrypointId,
            command: "command",
            next_block_id: null,
          },
        });
      }}>New command</button
    >
    <button
      on:click={() => {
        const newBlockId = `block-message-${userFlowConfig.blocks.length}`;
        userFlowConfig.node_display_coords[newBlockId] = newUserFlowNodePosition();
        userFlowConfig.blocks.push({
          message: {
            block_id: newBlockId,
            message_text: "Hello, I am bot!",
            next_block_id: null,
          },
        });
      }}>New message</button
    >
    <button on:click={() => console.log(userFlowConfig)}>Log current config</button>
  </div>
</div>

<style>
  .svelvet-container {
    width: 100%;
    height: 100vh;
  }

  div.custom-controls {
    position: fixed;
    left: 10px;
    top: 10px;
    background-color: white;
    border: 1px black solid;
    border-radius: 10px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-around;
    padding: 1em;
  }

  div.custom-controls > button {
    margin: 0.2em 0;
    width: 100%;
  }
</style>
