<!--
  Main node content container. Optionally runs a provided validator func on each 
  config update and if it detects errors, renders an error badge.
-->

<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { ActionIcon, Group, Space, Flex, Divider } from "@svelteuidev/core";
  import { Pencil1, Cross1 } from "radix-icons-svelte";
  import { languageConfigStore, type LanguageConfig } from "../stores";
  import { ok, type Result } from "../../utils";
  import type { ValidationError } from "../nodes/nodeValidators";
  import ErrorBadge from "../../components/ErrorBadge.svelte";
  import EllipsisText from "../../components/internal/EllipsisText.svelte";

  export let name: string;
  export let headerColor: string;
  export let config: any = null;
  export let isValid = true;
  export let configValidator: (config: any, langConfig: LanguageConfig | null) => Result<null, ValidationError> = (
    _,
    __,
  ) => ok(null);

  const dispatch = createEventDispatcher<{ edit: null; delete: null }>();

  const actionIconProps = {
    color: "dark",
    size: "sm",
    variant: "hover",
  };

  let configValidationResult: Result<null, ValidationError>;
  $: {
    configValidationResult = configValidator(config, $languageConfigStore);
    isValid = configValidationResult.ok;
  }
</script>

<div class="node-content-container">
  <Group
    spacing="xs"
    position="apart"
    override={{
      backgroundColor: headerColor,
      borderRadius: "10px 10px 0 0;",
      padding: "8px",
    }}
  >
    <EllipsisText override={{ fontWeight: "bold" }} maxWidth="200px">{name}</EllipsisText>
    <Space w="md" />
    <Flex>
      <ActionIcon {...actionIconProps} on:click={() => dispatch("edit")}>
        <Pencil1 />
      </ActionIcon>
      <ActionIcon {...actionIconProps} on:click={() => dispatch("delete")}>
        <Cross1 />
      </ActionIcon>
    </Flex>
  </Group>
  <Divider override={{ margin: 0 }} />
  <div class="node-content">
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
  }

  div.node-content {
    padding: 8px;
  }
</style>
