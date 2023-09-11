<script lang="ts">
  import { Svelvet } from "svelvet";

  import CommandEntryPointNode from "./nodes/CommandEntryPoint/Node.svelte";
  import MessageBlockNode from "./nodes/MessageBlock/Node.svelte";
  import DeletableEdge from "./components/DeletableEdge.svelte";

  import { saveBotConfig } from "../api/botConfig";
  import { getBlockId, getEntrypointId } from "../api/typeUtils";
  import type { BotConfig, UserFlowBlockConfig, UserFlowEntryPointConfig, UserFlowNodePosition } from "../api/types";

  import { getError, unwrap } from "../utils";
  import { findNewNodePosition } from "./utils";
  import {
    defaultCommandEntrypoint,
    defaultMessageBlockConfig,
    defaultHumanOperatorBlockCofig,
  } from "./nodes/defaultConfigs";
  import HumanOperatorNode from "./nodes/HumanOperatorBlock/Node.svelte";
  import { startBot } from "../api/lifecycle";

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

  function getEntrypointDestructor(idx: number) {
    return () => {
      userFlowConfig.entrypoints = userFlowConfig.entrypoints.toSpliced(idx, 1);
      const entrypointId = getEntrypointId(userFlowConfig.entrypoints[idx]);
      delete userFlowConfig.node_display_coords[entrypointId];
    };
  }
  function getEntrypointConstructor(prefix: string, entryPointConfigConstructor: (string) => UserFlowEntryPointConfig) {
    return () => {
      const id = `entrypoint-${prefix}-${crypto.randomUUID()}`;
      userFlowConfig.node_display_coords[id] = newUserFlowNodePosition();
      userFlowConfig.entrypoints.push(entryPointConfigConstructor(id));
    };
  }
  function getBlockDestructor(idx: number) {
    return () => {
      userFlowConfig.blocks = userFlowConfig.blocks.toSpliced(idx, 1);
      const blockId = getBlockId(userFlowConfig.blocks[idx]);
      delete userFlowConfig.node_display_coords[blockId];
    };
  }
  function getBlockConstructor(prefix: string, blockConfigConstructor: (string) => UserFlowBlockConfig) {
    return () => {
      const id = `block-${prefix}-${crypto.randomUUID()}`;
      userFlowConfig.node_display_coords[id] = newUserFlowNodePosition();
      userFlowConfig.blocks.push(blockConfigConstructor(id));
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
          on:delete={getEntrypointDestructor(idx)}
          bind:config={userFlowConfig.entrypoints[idx].command}
          bind:position={userFlowConfig.node_display_coords[entrypoint.command.entrypoint_id]}
        />
      {/if}
    {/each}
    {#each userFlowConfig.blocks as block, idx}
      {#if block.message !== null}
        <MessageBlockNode
          on:delete={getBlockDestructor(idx)}
          bind:config={userFlowConfig.blocks[idx].message}
          bind:position={userFlowConfig.node_display_coords[block.message.block_id]}
        />
      {:else if block.human_operator !== null}
        <HumanOperatorNode
          on:delete={getBlockDestructor(idx)}
          bind:config={userFlowConfig.blocks[idx].human_operator}
          bind:position={userFlowConfig.node_display_coords[block.human_operator.block_id]}
        />
      {/if}
    {/each}
  </Svelvet>
  <div class="custom-controls">
    <h3>{botName}</h3>
    <button on:click={getEntrypointConstructor("command", defaultCommandEntrypoint)}>New <b>command</b></button>
    <button on:click={getBlockConstructor("message", defaultMessageBlockConfig)}>New <b>message block</b></button>
    <button on:click={getBlockConstructor("human-opeartor", defaultHumanOperatorBlockCofig)}
      >New <b>human operator block</b></button
    >
    <button on:click={() => console.log(userFlowConfig)}>Log current config</button>
    <button on:click={saveCurrentBotConfig}>Save</button>
    <button on:click={() => startBot(botName)}>Run bot</button>
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
