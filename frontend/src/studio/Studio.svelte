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

  function newUserFlowNodePosition(): UserFlowNodePosition {
    const currentPositions = Object.values(botConfig.user_flow_config.node_display_coords);
    if (currentPositions.length === 0) {
      return { x: 0, y: 0 };
    } else {
      return findNewNodePosition(Object.values(botConfig.user_flow_config.node_display_coords), 200, 100, 30);
    }
  }

  function getEntrypointDestructor(id: string) {
    return () => {
      const idx = botConfig.user_flow_config.entrypoints
        .map(getEntrypointId)
        .findIndex((entrypointId) => entrypointId === id);
      console.debug(`Removing entrypoint ${id}, idx = ${idx}`);
      if (idx === -1) {
        console.log(`Entrypoing with id '${id}' not found`);
        return;
      }
      botConfig.user_flow_config.entrypoints = botConfig.user_flow_config.entrypoints.toSpliced(idx, 1);
      delete botConfig.user_flow_config.node_display_coords[id];
    };
  }
  function getEntrypointConstructor(
    prefix: string,
    entryPointConfigConstructor: (id: string) => UserFlowEntryPointConfig,
  ) {
    return () => {
      const id = `entrypoint-${prefix}-${crypto.randomUUID()}`;
      console.debug(`Creating new entrypoint ${id}`);
      botConfig.user_flow_config.node_display_coords[id] = newUserFlowNodePosition();
      botConfig.user_flow_config.entrypoints = [
        ...botConfig.user_flow_config.entrypoints,
        entryPointConfigConstructor(id),
      ];
    };
  }
  function getBlockDestructor(id: string) {
    return () => {
      const idx = botConfig.user_flow_config.blocks.map(getBlockId).findIndex((blockId) => blockId === id);
      console.debug(`Deleting block ${id}, idx = ${idx}`);
      if (idx === -1) {
        console.log(`Block with id '${id}' not found`);
        return;
      }
      botConfig.user_flow_config.blocks = botConfig.user_flow_config.blocks.toSpliced(idx, 1);
      delete botConfig.user_flow_config.node_display_coords[id];
    };
  }
  function getBlockConstructor(prefix: string, blockConfigConstructor: (id: string) => UserFlowBlockConfig) {
    return () => {
      const id = `block-${prefix}-${crypto.randomUUID()}`;
      console.debug(`Creating new block ${id}`);
      botConfig.user_flow_config.node_display_coords[id] = newUserFlowNodePosition();
      botConfig.user_flow_config.blocks = [...botConfig.user_flow_config.blocks, blockConfigConstructor(id)];
    };
  }

  async function saveCurrentBotConfig() {
    console.log(`Saving bot config for ${botName}`, botConfig);
    const res = await saveBotConfig(botName, botConfig);
    if (getError(res) !== null) {
      window.alert(`Error saving bot config: ${getError(res)}`);
    }
  }
</script>

<div class="svelvet-container">
  <Svelvet
    TD
    controls
    fitView={botConfig.user_flow_config.blocks.length + botConfig.user_flow_config.entrypoints.length > 0}
    edge={DeletableEdge}
  >
    {#each botConfig.user_flow_config.entrypoints as entrypoint, idx}
      {#if entrypoint.command !== null}
        <CommandEntryPointNode
          on:delete={getEntrypointDestructor(entrypoint.command.entrypoint_id)}
          bind:config={botConfig.user_flow_config.entrypoints[idx].command}
          bind:position={botConfig.user_flow_config.node_display_coords[entrypoint.command.entrypoint_id]}
        />
      {/if}
    {/each}
    {#each botConfig.user_flow_config.blocks as block, idx}
      {#if block.message !== null}
        <MessageBlockNode
          on:delete={getBlockDestructor(block.message.block_id)}
          bind:config={botConfig.user_flow_config.blocks[idx].message}
          bind:position={botConfig.user_flow_config.node_display_coords[block.message.block_id]}
        />
      {:else if block.human_operator !== null}
        <HumanOperatorNode
          on:delete={getBlockDestructor(block.human_operator.block_id)}
          bind:config={botConfig.user_flow_config.blocks[idx].human_operator}
          bind:position={botConfig.user_flow_config.node_display_coords[block.human_operator.block_id]}
        />
      {/if}
    {/each}
  </Svelvet>
  <div class="custom-controls">
    <h3>{botConfig.display_name}</h3>
    <button on:click={getEntrypointConstructor("command", defaultCommandEntrypoint)}>New <b>command</b></button>
    <button on:click={getBlockConstructor("message", defaultMessageBlockConfig)}>New <b>message block</b></button>
    <button on:click={getBlockConstructor("human-operator", defaultHumanOperatorBlockCofig)}
      >New <b>human operator block</b></button
    >
    <button on:click={() => console.log(botConfig.user_flow_config)}>Log current config</button>
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
