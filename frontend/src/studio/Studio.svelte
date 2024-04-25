<script lang="ts">
  import { Button, Heading, Spinner } from "flowbite-svelte";
  import { navigate } from "svelte-routing";
  import { Svelvet } from "svelvet";
  import { saveBotConfig } from "../api/botConfig";
  import { getBlockId, getEntrypointId } from "../api/typeUtils";
  import type { BotConfig, UserFlowEntryPointConfig } from "../api/types";
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

  export let botName: string;
  export let botConfig: BotConfig;
  export let readonly: boolean;

  const open = getModalOpener();

  // tracking when the config is modified to prevent exiting with unsaved changes
  let isConfigModified = false;
  let configReactivityTriggeredCount = 0;
  $: {
    botConfig; // trigger svelte's reactivity by mentioning the value we're reacting to
    configReactivityTriggeredCount += 1;
  }
  $: {
    if (configReactivityTriggeredCount > 2) {
      // dont know why it's 2 but it just works...
      isConfigModified = true;
    }
  }

  // setting the initial language config based on whether bot config includes language select block
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

  // factory for node deletion callbacks
  function nodeDeleter(id: string, postDelete: () => any = () => {}) {
    return () => {
      // this is a bit cumbersome because we store very similar things (blocks and entrypoing) in two different places
      // as a result we need to look in two places and process every one of them
      const entrypointIdx = botConfig.user_flow_config.entrypoints
        .map(getEntrypointId)
        .findIndex((nodeId) => nodeId === id);
      const blockIdx = botConfig.user_flow_config.blocks.map(getBlockId).findIndex((nodeId) => nodeId === id);
      if (entrypointIdx !== -1) {
        console.debug(
          `Deleting entrypoint id=${id} idx=${entrypointIdx}`,
          botConfig.user_flow_config.entrypoints[entrypointIdx],
        );
        botConfig.user_flow_config.entrypoints = botConfig.user_flow_config.entrypoints.toSpliced(entrypointIdx, 1);
      } else if (blockIdx !== -1) {
        console.debug(`Deleting block id=${id} idx=${blockIdx}`, botConfig.user_flow_config.blocks[blockIdx]);
        botConfig.user_flow_config.blocks = botConfig.user_flow_config.blocks.toSpliced(blockIdx, 1);
      } else {
        console.log(`Node with id '${id}' not found among entrypoints and blocks`);
        return;
      }
      delete botConfig.user_flow_config.node_display_coords[id];
      postDelete();
    };
  }

  // node creation machinery:
  // when the user clicks on "add" button for a particular kind of node, we save it as "tentative"
  // then, when the user selects a place for the node, we add it to the config
  enum NodeKind {
    BLOCK,
    ENTRYPOINT,
  }
  interface TentativeNode {
    kind: NodeKind;
    id: string;
    config: UserFlowEntryPointConfig | UserFlowEntryPointConfig;
  }
  let tentativeNode: TentativeNode | null = null;

  function nodeFactory(
    kind: NodeKind,
    prefix: string,
    configFactory: (
      id: string,
      langConfig: LanguageConfig | null,
    ) => UserFlowEntryPointConfig | UserFlowEntryPointConfig,
  ) {
    return () => {
      const nodeId = `${kind}-${prefix}-${crypto.randomUUID()}`;
      const config = configFactory(nodeId, $languageConfigStore);
      tentativeNode = {
        kind,
        id: nodeId,
        config,
      };
      console.debug(`Tentative node created`, tentativeNode);
    };
  }

  function customMouseDownHandler(e: MouseEvent, cursor: { x: number; y: number }): boolean {
    if (tentativeNode === null) return false;
    console.log("Mouse-down event received with tentative node set, processing, cursor=", cursor);
    if (e.button == 2) {
      console.debug("RMB click, tentative node dropped");
      tentativeNode = null;
      return true;
    }
    botConfig.user_flow_config.node_display_coords[tentativeNode.id] = {
      x: cursor.x - 125,
      y: cursor.y - 50,
    };
    if (tentativeNode.kind === NodeKind.BLOCK) {
      botConfig.user_flow_config.blocks = [...botConfig.user_flow_config.blocks, tentativeNode.config];
    } else {
      botConfig.user_flow_config.entrypoints = [...botConfig.user_flow_config.entrypoints, tentativeNode.config];
    }
    tentativeNode = null;
    return true;
  }

  // automatic config validation on any nodes' validity update
  let isNodeValid: { [k: string]: boolean } = {};
  let isConfigValid: boolean;
  $: {
    isConfigValid = !(
      botConfig.user_flow_config.blocks.some((block) => isNodeValid[getBlockId(block)] === false) ||
      botConfig.user_flow_config.entrypoints.some((ep) => isNodeValid[getEntrypointId(ep)] === false)
    );
  }

  // node saving function with "in progress" state
  let isSavingBotConfig = false;
  async function saveCurrentBotConfig(versionMessage: string | null, start: boolean) {
    if (readonly) return;
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
</script>

<div class="svelvet-container">
  <div class="navbar-container">
    <Navbar>
      <div class="flex gap-2">
        <Heading tag="h2" class="mr-2 max-w-96 text-ellipsis">
          {botConfig.display_name}
        </Heading>
        <Button
          disabled={readonly || !isConfigValid || !isConfigModified || isSavingBotConfig}
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
    {customMouseDownHandler}
  >
    <BotInfoNode {botName} bind:position={botConfig.user_flow_config.node_display_coords[BOT_INFO_NODE_ID]} />
    {#each botConfig.user_flow_config.entrypoints as entrypoint (getEntrypointId(entrypoint))}
      {#if entrypoint.command}
        <CommandEntryPointNode
          on:delete={nodeDeleter(entrypoint.command.entrypoint_id)}
          bind:config={entrypoint.command}
          bind:position={botConfig.user_flow_config.node_display_coords[entrypoint.command.entrypoint_id]}
          bind:isValid={isNodeValid[entrypoint.command.entrypoint_id]}
        />
      {/if}
    {/each}
    {#each botConfig.user_flow_config.blocks as block (getBlockId(block))}
      {#if block.content}
        <ContentBlockNode
          on:delete={nodeDeleter(block.content.block_id)}
          bind:config={block.content}
          bind:position={botConfig.user_flow_config.node_display_coords[block.content.block_id]}
          bind:isValid={isNodeValid[block.content.block_id]}
        />
      {:else if block.human_operator}
        <HumanOperatorNode
          {botName}
          on:delete={nodeDeleter(block.human_operator.block_id)}
          bind:config={block.human_operator}
          bind:position={botConfig.user_flow_config.node_display_coords[block.human_operator.block_id]}
          bind:isValid={isNodeValid[block.human_operator.block_id]}
        />
      {:else if block.language_select}
        <LanguageSelectNode
          on:delete={nodeDeleter(block.language_select.block_id, () => {
            languageConfigStore.set(null);
          })}
          bind:config={block.language_select}
          bind:position={botConfig.user_flow_config.node_display_coords[block.language_select.block_id]}
          bind:isValid={isNodeValid[block.language_select.block_id]}
        />
      {:else if block.menu}
        <MenuNode
          on:delete={nodeDeleter(block.menu.block_id)}
          bind:config={block.menu}
          bind:position={botConfig.user_flow_config.node_display_coords[block.menu.block_id]}
          bind:isValid={isNodeValid[block.menu.block_id]}
        />
      {:else if block.form}
        <FormNode
          {botName}
          on:delete={nodeDeleter(block.form.block_id)}
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
        on:click={nodeFactory(NodeKind.ENTRYPOINT, "command", defaultCommandEntrypoint)}
      />
      <AddNodeButton
        key={NodeTypeKey.content}
        on:click={nodeFactory(NodeKind.BLOCK, "content", defaultContentBlockConfig)}
      />
      <AddNodeButton
        key={NodeTypeKey.human_operator}
        on:click={nodeFactory(NodeKind.BLOCK, "human-operator", defaultHumanOperatorBlockConfig)}
      />
      <AddNodeButton
        key={NodeTypeKey.language_select}
        on:click={nodeFactory(NodeKind.BLOCK, "language-select", defaultLanguageSelectBlockConfig)}
      />
      <AddNodeButton key={NodeTypeKey.menu} on:click={nodeFactory(NodeKind.BLOCK, "menu", defaultMenuBlockConfig)} />
      <AddNodeButton key={NodeTypeKey.form} on:click={nodeFactory(NodeKind.BLOCK, "form", defaultFormBlockConfig)} />
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
