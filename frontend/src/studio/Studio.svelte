<script lang="ts">
  import { setContext } from "svelte";

  import { Button, Group, Stack } from "@svelteuidev/core";
  import { Svelvet } from "svelvet";
  import { navigate } from "svelte-routing";

  import CommandEntryPointNode from "./nodes/CommandEntryPoint/Node.svelte";
  import ContentBlockNode from "./nodes/ContentBlock/Node.svelte";
  import HumanOperatorNode from "./nodes/HumanOperatorBlock/Node.svelte";
  import LanguageSelectNode from "./nodes/LanguageSelectBlock/Node.svelte";
  import FormNode from "./nodes/FormBlock/Node.svelte";
  import StudioControls from "./StudioControls.svelte";
  import BotUserBadge from "../components/BotUserBadge.svelte";
  import EditableTitle from "./components/EditableTitle.svelte";
  import DeletableEdge from "./components/DeletableEdge.svelte";

  import { saveBotConfig } from "../api/botConfig";
  import { getBlockId, getEntrypointId } from "../api/typeUtils";
  import type { BotConfig, UserFlowBlockConfig, UserFlowEntryPointConfig, UserFlowNodePosition } from "../api/types";

  import { getError, withConfirmation } from "../utils";
  import { findNewNodePosition } from "./utils";
  import {
    defaultCommandEntrypoint,
    defaultContentBlockConfig,
    defaultFormBlockConfig,
    defaultHumanOperatorBlockCofig,
    defaultLanguageSelectBlockConfig,
  } from "./nodes/defaultConfigs";
  import { HUE, buttonColor } from "./nodes/colors";
  import { languageConfigStore } from "./stores";

  export let botName: string;
  export let botConfig: BotConfig;

  setContext("botName", botName);

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
  function getBlockDestructor(id: string, postDestruct: (() => void) | undefined = undefined) {
    return () => {
      const idx = botConfig.user_flow_config.blocks.map(getBlockId).findIndex((blockId) => blockId === id);
      console.debug(`Deleting block ${id}, idx = ${idx}`);
      if (idx === -1) {
        console.log(`Block with id '${id}' not found`);
        return;
      }
      botConfig.user_flow_config.blocks = botConfig.user_flow_config.blocks.toSpliced(idx, 1);
      delete botConfig.user_flow_config.node_display_coords[id];
      if (postDestruct !== undefined) postDestruct();
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

  let isNodeValid: { [k: string]: boolean } = {};
  let isConfigValid: boolean;
  $: {
    isConfigValid = !(
      botConfig.user_flow_config.blocks.some((block) => isNodeValid[getBlockId(block)] === false) ||
      botConfig.user_flow_config.entrypoints.some((ep) => isNodeValid[getEntrypointId(ep)] === false)
    );
  }

  let isSavingBotConfig = false;

  async function saveCurrentBotConfig() {
    if (!isConfigValid) return;
    isSavingBotConfig = true;
    console.log(`Saving bot config for ${botName}`, botConfig);
    const res = await saveBotConfig(botName, botConfig);
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
  <Svelvet
    TD
    controls
    fitView={botConfig.user_flow_config.blocks.length + botConfig.user_flow_config.entrypoints.length >= 1}
    edge={DeletableEdge}
  >
    {#each botConfig.user_flow_config.entrypoints as entrypoint, idx}
      {#if entrypoint.command}
        <CommandEntryPointNode
          on:delete={getEntrypointDestructor(entrypoint.command.entrypoint_id)}
          bind:config={entrypoint.command}
          bind:position={botConfig.user_flow_config.node_display_coords[entrypoint.command.entrypoint_id]}
          bind:isValid={isNodeValid[entrypoint.command.entrypoint_id]}
        />
      {/if}
    {/each}
    {#each botConfig.user_flow_config.blocks as block, idx}
      {#if block.content}
        <ContentBlockNode
          on:delete={getBlockDestructor(block.content.block_id)}
          bind:config={block.content}
          bind:position={botConfig.user_flow_config.node_display_coords[block.content.block_id]}
          bind:isValid={isNodeValid[block.content.block_id]}
        />
      {:else if block.human_operator}
        <HumanOperatorNode
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
      {:else if block.form}
        <FormNode
          on:delete={getBlockDestructor(block.form.block_id)}
          bind:config={block.form}
          bind:position={botConfig.user_flow_config.node_display_coords[block.form.block_id]}
          bind:isValid={isNodeValid[block.form.block_id]}
        />
      {/if}
    {/each}
  </Svelvet>
  <StudioControls title="Добавить" position="upper-left">
    <Group direction="column" spacing="xs">
      <Button
        compact
        variant="outline"
        color={buttonColor(HUE.command)}
        on:click={getEntrypointConstructor("command", defaultCommandEntrypoint)}
      >
        Команда
      </Button>
      <Button
        compact
        variant="outline"
        color={buttonColor(HUE.content)}
        on:click={getBlockConstructor("content", defaultContentBlockConfig)}>Контент</Button
      >
      <Button
        compact
        variant="outline"
        color={buttonColor(HUE.human_operator)}
        on:click={getBlockConstructor("human-operator", defaultHumanOperatorBlockCofig)}
      >
        Человек-оператор
      </Button>
      <Button
        compact
        disabled={$languageConfigStore !== null}
        variant="outline"
        color={buttonColor(HUE.language_select)}
        on:click={getBlockConstructor("language-select", defaultLanguageSelectBlockConfig)}
      >
        Выбор языка
      </Button>
      <Button
        compact
        variant="outline"
        color={buttonColor(HUE.form)}
        on:click={getBlockConstructor("form", defaultFormBlockConfig)}
      >
        Форма
      </Button>
    </Group>
  </StudioControls>
  <StudioControls position="upper-right">
    <Group noWrap spacing="xl">
      <Stack>
        <EditableTitle bind:title={botConfig.display_name} />
        <!-- <BotUserBadge {botName} /> -->
      </Stack>
      <Stack spacing="xs">
        <Button
          variant="filled"
          disabled={!isConfigValid || !isConfigModified}
          fullSize
          loading={isSavingBotConfig}
          on:click={saveCurrentBotConfig}
        >
          Сохранить
        </Button>
        <Button variant="outline" fullSize on:click={isConfigModified ? exitStudioWithConfirmation : exitStudio}>
          Выйти
        </Button>
      </Stack>
    </Group>
  </StudioControls>
</div>

<style>
  .svelvet-container {
    width: 100%;
    height: 100vh;
  }
</style>
