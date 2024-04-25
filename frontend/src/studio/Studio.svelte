<script lang="ts">
  import type { Writable } from "svelte/store";
  import { Button, Heading, Spinner } from "flowbite-svelte";
  import { onDestroy } from "svelte";
  import { navigate } from "svelte-routing";
  import { Svelvet, graphStore, type Graph, type XYPair } from "svelvet";
  import { saveBotConfig } from "../api/botConfig";
  import { getBlockId, getEntrypointId } from "../api/typeUtils";
  import type { BotConfig, UserFlowBlockConfig, UserFlowEntryPointConfig, UserFlowNodePosition } from "../api/types";
  import Navbar from "../components/Navbar.svelte";
  import { BOT_INFO_NODE_ID } from "../constants";
  import { getError, getModalOpener, withConfirmation } from "../utils";
  import SaveConfigModal from "./SaveConfigModal.svelte";
  import AddNodeButton from "./components/AddNodeButton.svelte";
  import DeletableEdge from "./components/DeletableEdge.svelte";
  import StudioSidePandel from "./components/StudioSidePanel.svelte";
  import BotInfoNode from "./nodes/BotInfo/Node.svelte";
  import CommandEntryPointNode from "./nodes/CommandEntryPoint/Node.svelte";
  import ContentBlockNode from "./nodes/ContentBlock/Node.svelte";
  import FormNode from "./nodes/FormBlock/Node.svelte";
  import HumanOperatorNode from "./nodes/HumanOperatorBlock/Node.svelte";
  import LanguageSelectNode from "./nodes/LanguageSelectBlock/Node.svelte";
  import MenuNode from "./nodes/MenuBlock/Node.svelte";
  import {
    defaultCommandEntrypoint,
    defaultContentBlockConfig,
    defaultFormBlockConfig,
    defaultHumanOperatorBlockConfig,
    defaultLanguageSelectBlockConfig,
    defaultMenuBlockConfig,
  } from "./nodes/defaultConfigs";
  import { NodeTypeKey } from "./nodes/display";
  import { languageConfigStore, type LanguageConfig } from "./stores";
  import { findNewNodePositionDown, findNewNodePositionRight } from "./utils";

  export let botName: string;
  export let botConfig: BotConfig;
  export let isSaveable: boolean;

  const open = getModalOpener();

  let configReactivityTriggeredCount = 0;
  $: {
    botConfig; // trigger svelte's reactivity by mentioning the value we're reacting to
    configReactivityTriggeredCount += 1;
  }
  let isConfigModified = false;
  $: {
    if (configReactivityTriggeredCount > 2) {
      // dont know why it's 2 but it just works...
      isConfigModified = true;
    }
  }

  // initial language config from the loaded config
  let languageSelectBlockFound = false;
  for (const block of botConfig.user_flow_config.blocks) {
    if (block.language_select) {
      languageSelectBlockFound = true;
      languageConfigStore.set({
        supportedLanguageCodes: block.language_select.supported_languages,
        defaultLanguageCode: block.language_select.default_language,
      });
    }
  }
  if (!languageSelectBlockFound) {
    languageConfigStore.set(null);
  }

  function newUserFlowNodePosition(isEntrypoing: boolean): UserFlowNodePosition {
    const currentPositions = Object.values(botConfig.user_flow_config.node_display_coords);
    if (currentPositions.length === 0) {
      return { x: 0, y: 0 };
    } else {
      const findFunc = isEntrypoing ? findNewNodePositionRight : findNewNodePositionDown;
      return findFunc(Object.values(botConfig.user_flow_config.node_display_coords), 250, 220, 30);
    }
  }

  function getEntrypointDestructor(id: string) {
    return () => {
      const idx = botConfig.user_flow_config.entrypoints
        .map(getEntrypointId)
        .findIndex((entrypointId) => entrypointId === id);
      if (idx === -1) {
        console.log(`Entrypoing with id '${id}' not found`);
        return;
      }
      console.debug(
        `Deleting entrypoint [idx = ${idx}] ${JSON.stringify(botConfig.user_flow_config.entrypoints[idx])}`,
      );
      botConfig.user_flow_config.entrypoints = botConfig.user_flow_config.entrypoints.toSpliced(idx, 1);
      delete botConfig.user_flow_config.node_display_coords[id];
    };
  }
  function getEntrypointConstructor(
    prefix: string,
    entryPointConfigConstructor: (id: string, langConfig: LanguageConfig | null) => UserFlowEntryPointConfig,
  ) {
    return () => {
      const id = `entrypoint-${prefix}-${crypto.randomUUID()}`;
      console.debug(`Creating new entrypoint ${id}`);
      botConfig.user_flow_config.node_display_coords[id] = newUserFlowNodePosition(true);
      botConfig.user_flow_config.entrypoints = [
        ...botConfig.user_flow_config.entrypoints,
        entryPointConfigConstructor(id, $languageConfigStore),
      ];
    };
  }
  function getBlockDestructor(id: string, postDestruct: (() => void) | undefined = undefined) {
    return () => {
      const idx = botConfig.user_flow_config.blocks.map(getBlockId).findIndex((blockId) => blockId === id);
      if (idx === -1) {
        console.log(`Block with id '${id}' not found`);
        return;
      }
      console.debug(`Deleting block [idx = ${idx}] ${JSON.stringify(botConfig.user_flow_config.blocks[idx])}`);
      botConfig.user_flow_config.blocks = botConfig.user_flow_config.blocks.toSpliced(idx, 1);
      delete botConfig.user_flow_config.node_display_coords[id];
      if (postDestruct !== undefined) postDestruct();
    };
  }
  function getBlockConstructor(
    prefix: string,
    blockConfigConstructor: (id: string, langConfig: LanguageConfig | null) => UserFlowBlockConfig,
  ) {
    return () => {
      const id = `block-${prefix}-${crypto.randomUUID()}`;
      console.debug(`Creating new block ${id}`);
      botConfig.user_flow_config.node_display_coords[id] = newUserFlowNodePosition(false);
      botConfig.user_flow_config.blocks = [
        ...botConfig.user_flow_config.blocks,
        blockConfigConstructor(id, $languageConfigStore),
      ];
    };
  }

  let isNodeValid: { [k: string]: boolean } = {};
  let isConfigValid: boolean;
  $: {
    isConfigValid = !(
      botConfig.user_flow_config.blocks.some((block) => isNodeValid[getBlockId(block)] === false) ||
      botConfig.user_flow_config.entrypoints.some((ep) => isNodeValid[getEntrypointId(ep)] === false)
    );
  }

  let isSavingBotConfig = false;

  async function saveCurrentBotConfig(versionMessage: string | null, start: boolean) {
    if (!isConfigValid) return;
    isSavingBotConfig = true;
    console.log(`Saving bot config for ${botName}`, botConfig);
    const res = await saveBotConfig(botName, { config: botConfig, version_message: versionMessage, start });
    isSavingBotConfig = false;
    if (getError(res) !== null) {
      window.alert(`Error saving bot config: ${getError(res)}`);
    }
    isConfigModified = false;
  }

  const exitStudio = () => navigate(`/#${botName}`);
  const exitStudioWithConfirmation = withConfirmation(
    "Вы уверены, что хотите выйти из студии? Несохранённые изменения будут потеряны.",
    async () => exitStudio(),
    "Выйти",
  );

  // HACK: we're hooking into Svelvet's internal writeables storing current graph translation and scale
  let translationStore: Writable<XYPair>;
  let scaleStore: Writable<number>;
  function hookIntoGraphTransformStores(graph: Graph) {
    translationStore = graph.transforms.translation;
    scaleStore = graph.transforms.scale;
  }

  function logCurrentTransform() {
    console.log("translation:", $translationStore, "scale:", $scaleStore);
  }
</script>

<div class="svelvet-container">
  <div class="navbar-container">
    <Navbar>
      <div class="flex gap-2">
        <Heading tag="h2" class="mr-2 max-w-96 text-ellipsis">
          {botConfig.display_name}
        </Heading>
        <Button
          disabled={!isSaveable || !isConfigValid || !isConfigModified || isSavingBotConfig}
          on:click={() => open(SaveConfigModal, { callback: saveCurrentBotConfig })}
        >
          {#if isSavingBotConfig}
            <Spinner class="me-3" size="4" color="white" />
          {/if}
          Сохранить
        </Button>
        <Button outline on:click={isConfigModified ? exitStudioWithConfirmation : exitStudio}>Выйти</Button>
      </div>
    </Navbar>
  </div>
  <Svelvet
    TD
    controls
    fitView={botConfig.user_flow_config.blocks.length + botConfig.user_flow_config.entrypoints.length >= 1}
    edge={DeletableEdge}
    editable={false}
    minimap={false}
    enableAllHotkeys={false}
    graphCallback={hookIntoGraphTransformStores}
  >
    <BotInfoNode {botName} bind:position={botConfig.user_flow_config.node_display_coords[BOT_INFO_NODE_ID]} />
    {#each botConfig.user_flow_config.entrypoints as entrypoint (getEntrypointId(entrypoint))}
      {#if entrypoint.command}
        <CommandEntryPointNode
          on:delete={getEntrypointDestructor(entrypoint.command.entrypoint_id)}
          bind:config={entrypoint.command}
          bind:position={botConfig.user_flow_config.node_display_coords[entrypoint.command.entrypoint_id]}
          bind:isValid={isNodeValid[entrypoint.command.entrypoint_id]}
        />
      {/if}
    {/each}
    {#each botConfig.user_flow_config.blocks as block (getBlockId(block))}
      {#if block.content}
        <ContentBlockNode
          on:delete={getBlockDestructor(block.content.block_id)}
          bind:config={block.content}
          bind:position={botConfig.user_flow_config.node_display_coords[block.content.block_id]}
          bind:isValid={isNodeValid[block.content.block_id]}
        />
      {:else if block.human_operator}
        <HumanOperatorNode
          {botName}
          on:delete={getBlockDestructor(block.human_operator.block_id)}
          bind:config={block.human_operator}
          bind:position={botConfig.user_flow_config.node_display_coords[block.human_operator.block_id]}
          bind:isValid={isNodeValid[block.human_operator.block_id]}
        />
      {:else if block.language_select}
        <LanguageSelectNode
          on:delete={getBlockDestructor(block.language_select.block_id, () => {
            languageConfigStore.set(null);
          })}
          bind:config={block.language_select}
          bind:position={botConfig.user_flow_config.node_display_coords[block.language_select.block_id]}
          bind:isValid={isNodeValid[block.language_select.block_id]}
        />
      {:else if block.menu}
        <MenuNode
          on:delete={getBlockDestructor(block.menu.block_id)}
          bind:config={block.menu}
          bind:position={botConfig.user_flow_config.node_display_coords[block.menu.block_id]}
          bind:isValid={isNodeValid[block.menu.block_id]}
        />
      {:else if block.form}
        <FormNode
          {botName}
          on:delete={getBlockDestructor(block.form.block_id)}
          bind:config={block.form}
          bind:position={botConfig.user_flow_config.node_display_coords[block.form.block_id]}
          bind:isValid={isNodeValid[block.form.block_id]}
        />
      {/if}
    {/each}
  </Svelvet>
  <StudioSidePandel>
    <div class="flex flex-col gap-3">
      <AddNodeButton
        key={NodeTypeKey.command}
        on:click={getEntrypointConstructor("command", defaultCommandEntrypoint)}
      />
      <AddNodeButton key={NodeTypeKey.content} on:click={getBlockConstructor("content", defaultContentBlockConfig)} />
      <AddNodeButton
        key={NodeTypeKey.human_operator}
        on:click={getBlockConstructor("human-operator", defaultHumanOperatorBlockConfig)}
      />
      <AddNodeButton
        key={NodeTypeKey.language_select}
        on:click={getBlockConstructor("language-select", defaultLanguageSelectBlockConfig)}
      />
      <AddNodeButton key={NodeTypeKey.menu} on:click={getBlockConstructor("menu", defaultMenuBlockConfig)} />

      <AddNodeButton key={NodeTypeKey.form} on:click={getBlockConstructor("form", defaultFormBlockConfig)} />
    </div>
  </StudioSidePandel>
</div>

<style>
  .svelvet-container {
    width: 100%;
    height: 100vh;
  }
  div.navbar-container {
    position: absolute;
    top: 0;
    z-index: 100;
    width: 100%;
  }
</style>
