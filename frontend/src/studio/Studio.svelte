<script lang="ts">
  import { Svelvet } from "svelvet";

  import CommandEntryPointNode from "./nodes/CommandEntryPoint/Node.svelte";
  import MessageBlockNode from "./nodes/MessageBlock/Node.svelte";
  import DeletableEdge from "./components/DeletableEdge.svelte";

  import { saveBotConfig } from "../api/botConfig";
  import { getBlockId, getEntrypointId } from "../api/typeUtils";
  import type { BotConfig, UserFlowNodePosition } from "../api/types";

  import { getError, unwrap } from "../utils";
  import { findNewNodePosition } from "./utils";

  export let botName: string;
  export let botConfig: BotConfig;

  const userFlowConfig = botConfig.user_flow_config;

  function newUserFlowNodePosition(): UserFlowNodePosition {
    const currentPositions = Object.values(userFlowConfig.node_display_coords);
    if (currentPositions.length === 0) {
      return { x: 0, y: 0 };
    } else {
      return findNewNodePosition(Object.values(userFlowConfig.node_display_coords), 200, 100, 30);
    }
  }

  function getOnDeleteEntrypoint(idx: number) {
    return () => {
      const entrypointId = getEntrypointId(userFlowConfig.entrypoints[idx]);
      userFlowConfig.entrypoints = userFlowConfig.entrypoints.toSpliced(idx, 1);
      delete userFlowConfig.node_display_coords[entrypointId];
    };
  }
  function getOnDeleteBlock(idx: number) {
    return () => {
      const blockId = getBlockId(userFlowConfig.blocks[idx]);
      userFlowConfig.blocks = userFlowConfig.blocks.toSpliced(idx, 1);
      delete userFlowConfig.node_display_coords[blockId];
    };
  }

  async function saveCurrentBotConfig() {
    const res = await saveBotConfig(botName, botConfig);
    if (getError(res) !== null) {
      window.alert(`Error saving bot config: ${getError(res)}`);
    } else {
      botConfig = unwrap(res);
    }
  }
</script>

<div class="svelvet-container">
  <Svelvet
    TD
    controls
    fitView={userFlowConfig.blocks.length + userFlowConfig.entrypoints.length > 0}
    edge={DeletableEdge}
  >
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
    <h3>{botName}</h3>
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
      }}>New <b>command</b></button
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
          human_operator: null,
        });
      }}>New <b>message block</b></button
    >
    <button
      on:click={() => {
        const newBlockId = `block-message-${userFlowConfig.blocks.length}`;
        userFlowConfig.node_display_coords[newBlockId] = newUserFlowNodePosition();
        userFlowConfig.blocks.push({
          message: null,
          human_operator: null,
        });
      }}>New <b>human operator block</b></button
    >
    <button on:click={() => console.log(userFlowConfig)}>Log current config</button>
    <button on:click={saveCurrentBotConfig}>Save</button>
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
  div.custom-controls > h3 {
    margin: 0.2em 0;
    width: 100%;
  }
</style>
