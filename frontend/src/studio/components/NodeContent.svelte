<!--
  Main node content container. Optionally runs a provided validator func on each 
  config update and if it detects errors, renders an error badge.
-->

<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { ActionIcon, Divider, Flex, Group, Space } from "@svelteuidev/core";
  import { PenOutline, TrashBinOutline } from "flowbite-svelte-icons";
  import { type LanguageConfig, languageConfigStore } from "../stores";
  import { getModalOpener, ok, type Result } from "../../utils";
  import type { ValidationError } from "../nodes/nodeValidators";
  import ErrorBadge from "../../components/ErrorBadge.svelte";
  import EllipsisText from "../../components/internal/EllipsisText.svelte";
  import { headerColor, NODE_HUE, NODE_ICON, NODE_TITLE, type NodeTypeKey } from "../nodes/display";

  export let key: NodeTypeKey;
  export let config: any = null;
  export let isValid = true;
  export let configValidator: (config: any, langConfig: LanguageConfig | null) => Result<null, ValidationError> = (
    _,
    __,
  ) => ok(null);

  const dispatch = createEventDispatcher<{ edit: null; delete: null }>();

  const actionIconProps = {
    color: "dark",
    size: "xs",
    variant: "hover",
  };

  let configValidationResult: Result<null, ValidationError>;
  $: {
    configValidationResult = configValidator(config, $languageConfigStore);
    isValid = configValidationResult.ok;
  }

  let isContentOverflown = false;

  function detectOverflow(node: HTMLElement) {
    // console.log(node);
    if (node.scrollHeight > node.clientHeight) {
      // console.log("DETECTED OVERFLOW");
      isContentOverflown = true;
    } else {
      isContentOverflown = false;
    }
  }

  const open = getModalOpener();
  function openErrorInModal() {
    if (!configValidationResult.ok) {
      open(ErrorBadge, { text: configValidationResult.error.error });
    }
  }
</script>

<div class="node-content-container">
  <!-- <div class="node-content-container" use:detectOverflow> -->
  <Group
    spacing="sm"
    position="apart"
    override={{
      backgroundColor: headerColor(NODE_HUE[key]),
      borderRadius: "10px 10px 0 0;",
      padding: "8px",
    }}
  >
    <Group spacing="xs" override={{ alignItems: "baseline" }}>
      <div class="icon-container">
        <svelte:component this={NODE_ICON[key]} />
      </div>
      <EllipsisText override={{ fontWeight: "bold" }} maxWidth="200px">{NODE_TITLE[key]}</EllipsisText>
    </Group>
    <Group spacing={5}>
      <ActionIcon {...actionIconProps} on:click={() => dispatch("edit")}>
        <PenOutline />
      </ActionIcon>
      <Space w="xs" />
      <ActionIcon {...actionIconProps} on:click={() => dispatch("delete")}>
        <TrashBinOutline />
      </ActionIcon>
    </Group>
  </Group>
  <Divider override={{ margin: 0 }} />
  <div class="node-content">
    {#if !configValidationResult.ok}
      <ErrorBadge text={configValidationResult.error.error} />
    {:else}
      <slot />
    {/if}
  </div>

  {#if isContentOverflown}
    <button
      class="overflow-ellipsis"
      style={configValidationResult.ok ? "" : "cursor:pointer;"}
      on:click={openErrorInModal}>{configValidationResult.ok ? "" : "..."}</button
    >
  {/if}
</div>

<style>
  div.node-content-container {
    width: 250px;
    /* max-height: 200px; */
    /* overflow-y: hidden; */
    /* position: relative; */
  }

  div.icon-container {
    width: 15px;
    height: 15px;
    display: flex;
    justify-content: center;
  }

  div.node-content {
    padding: 8px;
  }

  button.overflow-ellipsis {
    position: absolute;
    left: 0;
    bottom: 0;
    border-radius: 0 0 10px 10px;
    width: 100%;
    height: 2em;
    font-weight: 800;
    font-size: larger;
    background: linear-gradient(0deg, white, rgba(255, 255, 255, 0.9), transparent);
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    padding-bottom: 0.2em;
  }
</style>
