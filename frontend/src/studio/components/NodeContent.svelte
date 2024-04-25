<!--
  Main node content container. Optionally runs a provided validator func on each 
  config update and if it detects errors, renders an error badge.
-->

<script lang="ts">
  import { DotsHorizontalOutline, FileCopyOutline, PenOutline, TrashBinOutline } from "flowbite-svelte-icons";
  import { createEventDispatcher } from "svelte";
  import ActionIcon from "../../components/ActionIcon.svelte";
  import ErrorBadge from "../../components/ErrorBadge.svelte";
  import { ok, type Result } from "../../utils";
  import { NODE_HUE, NODE_ICON, NODE_TITLE, headerColor, type NodeTypeKey } from "../nodes/display";
  import type { ValidationError } from "../nodes/nodeValidators";
  import { languageConfigStore, type LanguageConfig } from "../stores";
  import { Popover } from "flowbite-svelte";

  export let key: NodeTypeKey;
  export let config: any = null;
  export let isValid = true;
  export let deletable = true;
  export let clonable = true;
  export let colorOverride: string | null = null;
  export let configValidator: (config: any, langConfig: LanguageConfig | null) => Result<null, ValidationError> = (
    _,
    __,
  ) => ok(null);

  const dispatch = createEventDispatcher<{ edit: null; delete: null; clone: null }>();

  let configValidationResult: Result<null, ValidationError>;
  $: {
    configValidationResult = configValidator(config, $languageConfigStore);
    isValid = configValidationResult.ok;
  }
</script>

<div class="node-content-container">
  <div
    class="flex flex-row gap-2 justify-between items-center p-2 border-b-2"
    style="background-color: {colorOverride || headerColor(NODE_HUE[key])}; border-radius: 10px 10px 0 0"
  >
    <div class="flex items-center gap-2">
      <svelte:component this={NODE_ICON[key]} class="w-4 h-4" />
      <span class="font-bold text-lg">{NODE_TITLE[key]}</span>
    </div>
    <div class="flex items-center gap-0">
      <ActionIcon icon={PenOutline} on:click={() => dispatch("edit")} />
      {#if deletable || clonable}
        <ActionIcon id="show-more-actions" icon={DotsHorizontalOutline} />
        <Popover triggeredBy="#show-more-actions" trigger="click" placement="right-start" class="m-0">
          {#if deletable}
            <ActionIcon icon={TrashBinOutline} on:click={() => dispatch("delete")} />
          {/if}
          {#if clonable}
            <ActionIcon icon={FileCopyOutline} on:click={() => dispatch("clone")} />
          {/if}
        </Popover>
      {/if}
    </div>
  </div>
  <div class="p-2">
    {#if !configValidationResult.ok}
      <ErrorBadge text={configValidationResult.error.error} />
    {:else}
      <slot />
    {/if}
  </div>
</div>

<style>
  div.node-content-container {
    width: 250px;
    /* this is quick and dirty, better solution for overflowing blocks needed */
    max-height: 250px;
    text-overflow: ellipsis;
    overflow-y: hidden;
  }
</style>
