<!--
  Main node content container. Optionally runs a provided validator func on each 
  config update and if it detects errors, renders an error badge.
-->

<script lang="ts">
  import { DotsHorizontalOutline, FileCopyOutline, PenOutline, TrashBinOutline } from "flowbite-svelte-icons";
  import { createEventDispatcher } from "svelte";
  import ActionIcon from "../../components/ActionIcon.svelte";
  import ErrorBadge from "../../components/AlertBadge.svelte";
  import { ok, type Result } from "../../utils";
  import { NODE_HUE, NODE_ICON, NODE_TITLE, headerColor, type NodeTypeKey } from "../nodes/display";
  import type { ValidationError } from "../nodes/nodeValidators";
  import { languageConfigStore, type LanguageConfig } from "../stores";
  import { Listgroup, ListgroupItem, Popover } from "flowbite-svelte";

  export let id: string;
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

  const dispatch = createEventDispatcher<{ edit: string; delete: string; clone: string }>();

  let configValidationResult: Result<null, ValidationError>;
  $: {
    configValidationResult = configValidator(config, $languageConfigStore);
    isValid = configValidationResult.ok;
  }

  const showMoreActionsIconId = `show-more-actions-${id}-${crypto.randomUUID()}`;
</script>

<div class="node-content-container">
  <div
    class="flex flex-row gap-2 justify-between items-center p-2 rounded-none"
    style="background-color: {colorOverride || headerColor(NODE_HUE[key])}"
  >
    <div class="flex items-center gap-2">
      <svelte:component this={NODE_ICON[key]} class="w-4 h-4" />
      <span class="font-bold text-lg">{NODE_TITLE[key]}</span>
    </div>
    <div class="flex items-center gap-0">
      <ActionIcon icon={PenOutline} on:click={() => dispatch("edit", id)} />
      {#if deletable || clonable}
        <ActionIcon id={showMoreActionsIconId} icon={DotsHorizontalOutline} />
        <Popover triggeredBy={"#" + showMoreActionsIconId} placement="right-start" defaultClass="">
          <Listgroup active class="text-sm border-none">
            <!-- debugging -->
            <!-- <ListgroupItem active={false}>{id}</ListgroupItem> -->
            {#if clonable}
              <ListgroupItem on:click={() => dispatch("clone", id)} class="gap-2">
                <FileCopyOutline class="w-3 h-3 text-gray-700" />
                Дублировать
              </ListgroupItem>
            {/if}
            {#if deletable}
              <ListgroupItem on:click={() => dispatch("delete", id)} class="gap-2">
                <TrashBinOutline class="w-3 h-3 text-gray-700" />
                Удалить
              </ListgroupItem>
            {/if}
          </Listgroup>
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
    overflow-y: hidden;
  }
</style>
