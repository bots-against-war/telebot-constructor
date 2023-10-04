<script lang="ts">
  import { Node } from "svelvet";
  import type { ContentBlock } from "../../../api/types";
  import NodeContent from "../../components/NodeContent.svelte";
  import OutputAnchor from "../../components/OutputAnchor.svelte";
  import InputAnchor from "../../components/InputAnchor.svelte";
  import type { SvelvetPosition } from "../../../types";

  import Modal from "./Modal.svelte";
  import { getModalOpener } from "../../../utils";
  import { DEFAULT_NODE_PROPS } from "../nodeProps";
  const openModal = getModalOpener();

  export let config: ContentBlock;
  export let position: SvelvetPosition;
  const setNewConfig = (newConfig: ContentBlock) => {
    config = newConfig;
  };
</script>

<Node id={config.block_id} bind:position {...DEFAULT_NODE_PROPS}>
  <InputAnchor />
  <NodeContent
    name="Контент"
    headerColor="#62B1D0"
    on:delete
    on:edit={() =>
      openModal(Modal, {
        config,
        onConfigUpdate: setNewConfig,
      })}
  >
    <span>{config.contents[0].text?.text}</span>
  </NodeContent>
  <OutputAnchor bind:nextBlockId={config.next_block_id} />
</Node>
