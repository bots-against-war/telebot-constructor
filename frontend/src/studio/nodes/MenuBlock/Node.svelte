<script lang="ts">
  import { Node } from "svelvet";
  import type { MenuBlock } from "../../../api/types";
  import type { SvelvetPosition } from "../../../types";
  import { getModalOpener } from "../../../utils";
  import InputAnchor from "../../components/InputAnchor.svelte";
  import LocalizableText from "../../components/LocalizableText.svelte";
  import NodeContent from "../../components/NodeContent.svelte";
  import OutputAnchor from "../../components/OutputAnchor.svelte";
  import OutputAnchorsBox from "../../components/OutputAnchorsBox.svelte";
  import { languageConfigStore } from "../../stores";
  import { localizableTextToString } from "../../utils";
  import { NodeTypeKey } from "../display";
  import { DEFAULT_NODE_PROPS } from "../nodeProps";
  import { validateMenuBlock } from "../nodeValidators";
  import Modal from "./Modal.svelte";

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
    key={NodeTypeKey.menu}
    {config}
    bind:isValid
    configValidator={validateMenuBlock}
    on:delete
    on:clone
    on:edit={openEditModal}
  >
    <LocalizableText text={config.menu.text} />
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
