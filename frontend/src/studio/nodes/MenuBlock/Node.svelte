<script lang="ts">
  import { Node } from "svelvet";
  import type { ContentBlock, MenuBlock } from "../../../api/types";
  import NodeContent from "../../components/NodeContent.svelte";
  import OutputAnchor from "../../components/OutputAnchor.svelte";
  import InputAnchor from "../../components/InputAnchor.svelte";
  import type { SvelvetPosition } from "../../../types";

  import Modal from "./Modal.svelte";
  import { getModalOpener } from "../../../utils";
  import { DEFAULT_NODE_PROPS } from "../nodeProps";
  import { HUE, headerColor } from "../colors";
  import { validateMenuBlock } from "../nodeValidators";
  import OutputAnchorsBox from "../../components/OutputAnchorsBox.svelte";
  import { localizableTextToString } from "../../utils";
  import { languageConfigStore } from "../../stores";
  const openModal = getModalOpener();

  export let config: MenuBlock;
  export let position: SvelvetPosition;
  export let isValid = true;

  const setNewConfig = (newConfig: MenuBlock) => {
    config = newConfig;
  };
  const openEditModal = () =>
    openModal(Modal, {
      config,
      onConfigUpdate: setNewConfig,
    });
</script>

<Node id={config.block_id} bind:position {...DEFAULT_NODE_PROPS}>
  <InputAnchor />
  <NodeContent
    name="Меню"
    headerColor={headerColor(HUE.menu)}
    {config}
    bind:isValid
    configValidator={validateMenuBlock}
    on:delete
    on:edit={openEditModal}
  >
    TBD
  </NodeContent>
  <OutputAnchorsBox>
    {#each config.menu.items as item (item.label)}
      {#if item.next_block_id !== undefined}
        <OutputAnchor
          bind:nextBlockId={item.next_block_id}
          anchorLabel={localizableTextToString(item.label, $languageConfigStore)}
        />
      {/if}
    {/each}
  </OutputAnchorsBox>
</Node>
