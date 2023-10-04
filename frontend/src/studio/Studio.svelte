<script lang="ts">
  import { Svelvet } from "svelvet";
  import { Button, Group } from "@svelteuidev/core";

  import CommandEntryPointNode from "./nodes/CommandEntryPoint/Node.svelte";
  import ContentBlockNode from "./nodes/ContentBlock/Node.svelte";
  import DeletableEdge from "./components/DeletableEdge.svelte";

  import { saveBotConfig } from "../api/botConfig";
  import { getBlockId, getEntrypointId } from "../api/typeUtils";
  import type { BotConfig, UserFlowBlockConfig, UserFlowEntryPointConfig, UserFlowNodePosition } from "../api/types";

  import { getError } from "../utils";
  import { findNewNodePosition } from "./utils";
  import {
    defaultCommandEntrypoint,
    defaultContentBlockConfig,
    defaultHumanOperatorBlockCofig,
  } from "./nodes/defaultConfigs";
  import HumanOperatorNode from "./nodes/HumanOperatorBlock/Node.svelte";
  import StudioControls from "./StudioControls.svelte";
  import { navigate } from "svelte-routing";
  import { setContext } from "svelte";

  export let botName: string;
  export let botConfig: BotConfig;

  setContext("botName", botName);

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

  let isSavingBotConfig = false;

  async function saveCurrentBotConfig() {
    isSavingBotConfig = true;
    console.log(`Saving bot config for ${botName}`, botConfig);
    const res = await saveBotConfig(botName, botConfig);
    isSavingBotConfig = false;
    if (getError(res) !== null) {
      window.alert(`Error saving bot config: ${getError(res)}`);
    }
  }
</script>

<div class="svelvet-container">
  <Svelvet
    TD
    controls
    fitView={botConfig.user_flow_config.blocks.length + botConfig.user_flow_config.entrypoints.length >= 1}
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
      {#if block.content !== null}
        <ContentBlockNode
          on:delete={getBlockDestructor(block.content.block_id)}
          bind:config={botConfig.user_flow_config.blocks[idx].content}
          bind:position={botConfig.user_flow_config.node_display_coords[block.content.block_id]}
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
  <StudioControls title="Добавить" position="upper-left">
    <Group direction="column" spacing="xs">
      <!-- TODO: styling of buttons for each block type -->
      <Button compact color="gray" on:click={getEntrypointConstructor("command", defaultCommandEntrypoint)}>
        Команда
      </Button>
      <Button compact color="gray" on:click={getBlockConstructor("content", defaultContentBlockConfig)}>Контент</Button>
      <Button compact color="gray" on:click={getBlockConstructor("human-operator", defaultHumanOperatorBlockCofig)}>
        Человек-оператор
      </Button>
    </Group>
  </StudioControls>
  <StudioControls position="upper-right">
    <Group direction="column" spacing="xs">
      <Button variant="filled" fullSize loading={isSavingBotConfig} on:click={saveCurrentBotConfig}>Сохранить</Button>
      <Button variant="outline" fullSize on:click={() => navigate(`/#${botName}`)}>Выйти</Button>
    </Group>
  </StudioControls>
</div>

<style>
  .svelvet-container {
    width: 100%;
    height: 100vh;
  }
</style>
