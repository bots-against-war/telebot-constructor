<script lang="ts">
  import { Button, Heading, Spinner, Tooltip } from "flowbite-svelte";
  import { navigate } from "svelte-routing";
  import { Svelvet } from "svelvet";
  import { saveBotConfig } from "../api/botConfig";
  import { getBlockId, getEntrypointId } from "../api/typeUtils";
  import type { BotConfig, UserFlowEntryPointConfig } from "../api/types";
  import Navbar from "../components/Navbar.svelte";
  import { BOT_INFO_NODE_ID } from "../constants";
  import { dashboardPath } from "../routeUtils";
  import { INFO_MODAL_OPTIONS, err, getError, getModalOpener, ok, withConfirmation, type Result } from "../utils";
  import ReadmeModal from "./ReadmeModal.svelte";
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
  import { NODE_HUE, NODE_ICON, NODE_TITLE, NodeTypeKey, headerColor } from "./nodes/display";
  import { languageConfigStore, type LanguageConfig } from "./stores";
  import {
    NodeKind,
    clone,
    cloneBlockConfig,
    cloneEntrypointConfig,
    filterNodeDisplayCoords,
    generateNodeId,
    type TentativeNode,
  } from "./utils";
  import { QuestionCircleOutline } from "flowbite-svelte-icons";

  export let botId: string;
  export let botConfig: BotConfig;
  export let readonly: boolean;

  const open = getModalOpener();

  // we store node positions separately to be able to react to bot config changes with sveltes $:{} blocks,
  // while ignoring changes in the noisy and unimportant node position data
  // this way, node movement doesn't trigger any logic reactive to bot config
  // when we save / load bot config, we manually add display coords to it
  let nodeDisplayCoords = botConfig.user_flow_config.node_display_coords;

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

  // saving bot config copy on every update for ctrl+Z functionality
  const botConfigEditHistory: BotConfig[] = [];
  const EDIT_HISTORY_LENGTH = 30;
  let lastEditSavedAt: number | null = null;
  $: {
    const configClone = clone(botConfig);
    const now = Date.now();
    if (botConfigEditHistory.length > 0 && (lastEditSavedAt === null || now - lastEditSavedAt < 100)) {
      console.debug("Overwriting the last change in edit history with ", configClone);
      botConfigEditHistory[botConfigEditHistory.length - 1] = configClone;
    } else {
      console.debug("Pushing bot config to edit history: ", configClone);
      botConfigEditHistory.push(configClone);
      if (botConfigEditHistory.length > EDIT_HISTORY_LENGTH) {
        botConfigEditHistory.splice(0, botConfigEditHistory.length - EDIT_HISTORY_LENGTH);
      }
      lastEditSavedAt = now;
    }
  }

  function undo() {
    if (botConfigEditHistory.length < 2) {
      console.debug("Already at the last change, nothing to undo");
      return;
    }
    console.debug("Undoing the last change...");
    botConfigEditHistory.pop();
    const prevBotConfig = botConfigEditHistory.pop();
    if (prevBotConfig) {
      prevBotConfig.user_flow_config.node_display_coords = filterNodeDisplayCoords(
        { ...prevBotConfig.user_flow_config.node_display_coords, ...nodeDisplayCoords },
        prevBotConfig,
      );
      botConfig = prevBotConfig;
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

  // node deletion callback
  function deleteNode(event: CustomEvent<string>) {
    const id = event.detail;
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
      console.debug(`Node with id '${id}' not found among entrypoints and blocks`);
      return;
    }
  }

  // node creation machinery:
  // when the user clicks on "add" button for a particular kind of node, we save it as "tentative"
  // then, when the user selects a place for the node, we add it to the config

  let tentativeNode: TentativeNode | null = null;

  function nodeFactory(
    kind: NodeKind,
    typeKey: NodeTypeKey,
    configFactory: (
      id: string,
      langConfig: LanguageConfig | null,
    ) => UserFlowEntryPointConfig | UserFlowEntryPointConfig,
  ) {
    return () => {
      const nodeId = generateNodeId(kind, typeKey);
      const config = configFactory(nodeId, $languageConfigStore);
      tentativeNode = {
        kind,
        typeKey,
        id: nodeId,
        config,
      };
      console.debug(`Tentative node created`, tentativeNode);
    };
  }

  function customMouseDownHandler(e: MouseEvent, cursor: { x: number; y: number }): boolean {
    if (tentativeNode === null) return false;
    console.debug("Mouse-down event received with tentative node set, processing, cursor=", cursor);
    if (e.button == 2) {
      console.debug("RMB click, tentative node dropped");
      tentativeNode = null;
      return true;
    }
    nodeDisplayCoords[tentativeNode.id] = {
      x: cursor.x - 125, // half-width of the node in svelvet's coords
      y: cursor.y - 50, // just some arbitrary offset
    };
    if (tentativeNode.kind === NodeKind.block) {
      botConfig.user_flow_config.blocks = [...botConfig.user_flow_config.blocks, tentativeNode.config];
    } else {
      botConfig.user_flow_config.entrypoints = [...botConfig.user_flow_config.entrypoints, tentativeNode.config];
    }
    tentativeNode = null;
    return true;
  }

  // node cloning is another way to create nodes from existing one
  function cloneNode(event: CustomEvent<string>) {
    const id = event.detail;
    const entrypointIdx = botConfig.user_flow_config.entrypoints.map(getEntrypointId).findIndex((eId) => eId === id);
    const blockIdx = botConfig.user_flow_config.blocks.map(getBlockId).findIndex((bId) => bId === id);
    if (entrypointIdx !== -1) {
      tentativeNode = cloneEntrypointConfig(botConfig.user_flow_config.entrypoints[entrypointIdx]);
    } else if (blockIdx !== -1) {
      tentativeNode = cloneBlockConfig(botConfig.user_flow_config.blocks[blockIdx]);
    } else {
      console.debug(`Node with id '${id}' not found among entrypoints and blocks`);
      return;
    }
  }

  // automatic config validation on any nodes' validity update
  let isNodeValid: { [k: string]: boolean } = {};
  let configValidationResult: Result<null> = ok(null);
  $: {
    configValidationResult = ok(null);
    if (
      botConfig.user_flow_config.blocks.some((b) => !isNodeValid[getBlockId(b)]) ||
      botConfig.user_flow_config.entrypoints.some((e) => !isNodeValid[getEntrypointId(e)])
    ) {
      configValidationResult = err("Проблема в одном или нескольких блоках");
    }
    const occurrenceCounts = botConfig.user_flow_config.entrypoints
      .map((ep) => ep.command?.command)
      .filter((cmd) => cmd !== undefined)
      .reduce((acc: { [k: string]: number }, cmd) => {
        if (cmd) acc[cmd] = 1 + (acc[cmd] || 0);
        return acc;
      }, {});

    if (Object.values(occurrenceCounts).some((v) => v > 1)) {
      configValidationResult = err("Бот содержит повторяющиеся /команды");
    }
  }

  // node saving function with "in progress" state
  let isSavingBotConfig = false;
  async function saveCurrentBotConfig(versionMessage: string | null, start: boolean) {
    if (readonly) return;
    if (!configValidationResult.ok) return;
    isSavingBotConfig = true;
    console.debug(`Saving bot config for ${botId}`, botConfig);
    // returning node display coords from separate storage to config
    botConfig.user_flow_config.node_display_coords = filterNodeDisplayCoords(
      { ...botConfig.user_flow_config.node_display_coords, ...nodeDisplayCoords },
      botConfig,
    );
    const res = await saveBotConfig(botId, { config: botConfig, version_message: versionMessage, start });
    isSavingBotConfig = false;
    if (getError(res) !== null) {
      window.alert(`Error saving bot config: ${getError(res)}`);
    } else {
      isConfigModified = false;
    }
  }

  const exitStudio = () => navigate(dashboardPath(botId));
  const exitStudioWithConfirmation = withConfirmation(
    "Вы уверены, что хотите выйти из студии? Несохранённые изменения будут потеряны.",
    async () => exitStudio(),
    "Выйти",
  );

  let tentativeNodeMouseFollowerElement: HTMLElement | null = null;
  function handleMouseMove(e: MouseEvent) {
    if (!tentativeNodeMouseFollowerElement) return;
    tentativeNodeMouseFollowerElement.style.left = e.pageX + "px";
    tentativeNodeMouseFollowerElement.style.top = e.pageY + "px";
  }

  const openReadmeModal = () => open(ReadmeModal, {}, INFO_MODAL_OPTIONS);
  const README_SHOWN_LS_KEY = "readmeShown";
  if (localStorage.getItem(README_SHOWN_LS_KEY) === null) {
    localStorage.setItem(README_SHOWN_LS_KEY, "yea");
    openReadmeModal();
  }
</script>

<svelte:window
  on:mousemove={handleMouseMove}
  on:keydown={(e) => {
    if (
      e.target &&
      // @ts-expect-error
      e.target.tagName !== "TEXTAREA" &&
      // @ts-expect-error
      e.target.tagName !== "INPUT" &&
      !e.repeat &&
      (e.metaKey || e.ctrlKey) &&
      e.code === "KeyZ"
    ) {
      undo();
    }
  }}
/>
<div class="svelvet-container">
  <div class="navbar-container">
    <Navbar>
      <div class="flex gap-2">
        <Heading tag="h3" class="mr-2 max-w-96 text-nowrap text-ellipsis overflow-clip" title={botConfig.display_name}>
          {botConfig.display_name}
        </Heading>
        {#if readonly || !configValidationResult.ok || !isConfigModified}
          <Tooltip placement="bottom" triggeredBy="#save-button"
            >{readonly
              ? "Режим просмотра"
              : !configValidationResult.ok
                ? "Ошибка валидации: " + getError(configValidationResult)
                : "Нет изменений"}</Tooltip
          >
        {/if}
        <Button
          id="save-button"
          disabled={readonly || !configValidationResult.ok || !isConfigModified || isSavingBotConfig}
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
    fitView={botConfig.user_flow_config.blocks.length + botConfig.user_flow_config.entrypoints.length >= 1}
    edge={DeletableEdge}
    editable={false}
    minimap={false}
    enableAllHotkeys={false}
    controls
    trackpadPan
    {customMouseDownHandler}
    customCssCursor={tentativeNode ? "crosshair" : null}
  >
    <BotInfoNode {botId} bind:position={nodeDisplayCoords[BOT_INFO_NODE_ID]} />
    {#each botConfig.user_flow_config.entrypoints as entrypoint (getEntrypointId(entrypoint))}
      {#if entrypoint.command}
        <CommandEntryPointNode
          on:delete={deleteNode}
          bind:config={entrypoint.command}
          bind:position={nodeDisplayCoords[entrypoint.command.entrypoint_id]}
          bind:isValid={isNodeValid[entrypoint.command.entrypoint_id]}
        />
      {/if}
    {/each}
    {#each botConfig.user_flow_config.blocks as block (getBlockId(block))}
      {#if block.content}
        <ContentBlockNode
          on:delete={deleteNode}
          on:clone={cloneNode}
          bind:config={block.content}
          bind:position={nodeDisplayCoords[block.content.block_id]}
          bind:isValid={isNodeValid[block.content.block_id]}
        />
      {:else if block.human_operator}
        <HumanOperatorNode
          {botId}
          on:delete={deleteNode}
          on:clone={cloneNode}
          bind:config={block.human_operator}
          bind:position={nodeDisplayCoords[block.human_operator.block_id]}
          bind:isValid={isNodeValid[block.human_operator.block_id]}
        />
      {:else if block.language_select}
        <LanguageSelectNode
          on:delete={(e) => {
            deleteNode(e);
            languageConfigStore.set(null);
          }}
          bind:config={block.language_select}
          bind:position={nodeDisplayCoords[block.language_select.block_id]}
          bind:isValid={isNodeValid[block.language_select.block_id]}
        />
      {:else if block.menu}
        <MenuNode
          on:delete={deleteNode}
          on:clone={cloneNode}
          bind:config={block.menu}
          bind:position={nodeDisplayCoords[block.menu.block_id]}
          bind:isValid={isNodeValid[block.menu.block_id]}
        />
      {:else if block.form}
        <FormNode
          {botId}
          on:delete={deleteNode}
          on:clone={cloneNode}
          bind:config={block.form}
          bind:position={nodeDisplayCoords[block.form.block_id]}
          bind:isValid={isNodeValid[block.form.block_id]}
        />
      {/if}
    {/each}
  </Svelvet>
  <StudioSidePandel>
    <div class="flex flex-col gap-3">
      <AddNodeButton
        key={NodeTypeKey.command}
        on:click={nodeFactory(NodeKind.entrypoint, NodeTypeKey.command, defaultCommandEntrypoint)}
      />
      <AddNodeButton
        key={NodeTypeKey.content}
        on:click={nodeFactory(NodeKind.block, NodeTypeKey.content, defaultContentBlockConfig)}
      />
      <AddNodeButton
        key={NodeTypeKey.human_operator}
        on:click={nodeFactory(NodeKind.block, NodeTypeKey.human_operator, defaultHumanOperatorBlockConfig)}
      />
      <AddNodeButton
        key={NodeTypeKey.language_select}
        on:click={nodeFactory(NodeKind.block, NodeTypeKey.language_select, defaultLanguageSelectBlockConfig)}
      />
      <AddNodeButton
        key={NodeTypeKey.menu}
        on:click={nodeFactory(NodeKind.block, NodeTypeKey.menu, defaultMenuBlockConfig)}
      />
      <AddNodeButton
        key={NodeTypeKey.form}
        on:click={nodeFactory(NodeKind.block, NodeTypeKey.form, defaultFormBlockConfig)}
      />
      <Button on:click={openReadmeModal}>
        <QuestionCircleOutline class="w-4 h-4 mr-2" />
        Инструкции
      </Button>
    </div>
  </StudioSidePandel>
  {#if tentativeNode}
    <div
      id="tentative-node-mouse-follower"
      style="background-color: {headerColor(NODE_HUE[tentativeNode.typeKey])}"
      bind:this={tentativeNodeMouseFollowerElement}
    >
      <div class="flex items-center gap-2">
        <svelte:component this={NODE_ICON[tentativeNode.typeKey]} class="w-4 h-4" />
        <span class="font-bold text-lg">{NODE_TITLE[tentativeNode.typeKey]}</span>
      </div>
    </div>
  {/if}
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
  #tentative-node-mouse-follower {
    opacity: 0.8;
    position: absolute;
    top: -300px;
    left: -300px;
    /* x, y of cursor should be above in the center */
    transform: translate(-50%, -140%);
    /* mimicking node styles */
    background-color: white;
    border-radius: 0;
    border: solid 1px rgb(206, 212, 218);
    padding: 8px;
  }
</style>
