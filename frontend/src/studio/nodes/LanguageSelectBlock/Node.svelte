<script lang="ts">
  import { Group } from "@svelteuidev/core";
  import { Node } from "svelvet";

  import type { SvelvetPosition } from "../../../types";
  import type { LanguageSelectBlock } from "../../../api/types";
  import { getModalOpener } from "../../../utils";

  import Modal from "./Modal.svelte";
  import NodeContent from "../../components/NodeContent.svelte";
  import InputAnchor from "../../components/InputAnchor.svelte";
  import OutputAnchor from "../../components/OutputAnchor.svelte";
  import { DEFAULT_NODE_PROPS } from "../nodeProps";
  import { HUE, headerColor } from "../colors";
  import LanguageBadge from "../../../components/LanguageBadge.svelte";
  import ErrorBadge from "../../../components/ErrorBadge.svelte";

  const openModal = getModalOpener();

  export let config: LanguageSelectBlock;
  export let position: SvelvetPosition;

  const setNewConfig = (newConfig: LanguageSelectBlock) => {
    config = newConfig;
    console.log("HO config updated");
    console.log(config);
  };
  const openEditModal = () =>
    openModal(Modal, {
      config,
      onConfigUpdate: setNewConfig,
    });

  if (config.supported_languages.length === 0) {
    openEditModal();
  }
</script>

<Node id={config.block_id} bind:position {...DEFAULT_NODE_PROPS}>
  <InputAnchor />
  <NodeContent name="Выбор языка" headerColor={headerColor(HUE.language_select)} on:delete on:edit={openEditModal}>
    {#if config.supported_languages.length === 0}
      <ErrorBadge text="Нужно выбрать хотя бы один язык" />
    {:else}
      <Group spacing="xs" override={{ maxWidth: "300px" }}>
        {#each config.supported_languages as language}
          <LanguageBadge {language} />
        {/each}
      </Group>
    {/if}
  </NodeContent>
  <OutputAnchor bind:nextBlockId={config.language_selected_next_block_id} />
</Node>
