<script lang="ts">
  import { Node } from "svelvet";
  import type { ContentBlock } from "../../../api/types";
  import NodeContent from "../../components/NodeContent.svelte";
  import OutputAnchor from "../../components/OutputAnchor.svelte";
  import InputAnchor from "../../components/InputAnchor.svelte";
  import type { SvelvetPosition } from "../../../types";

  import Modal from "./Modal.svelte";
  import { getModalOpener } from "../../../utils";
  const openModal = getModalOpener();

  export let config: ContentBlock;
  export let position: SvelvetPosition;
  const setNewConfig = (newConfig: ContentBlock) => {
    config = newConfig;
  };
</script>

<Node id={config.block_id} bgColor="#bfebff" bind:position>
  <InputAnchor />
  <NodeContent
    name="Контент"
    on:delete
    on:edit={() =>
      openModal(Modal, {
        config,
        onConfigUpdate: setNewConfig,
      })}
  >
    <span>{config.contents[0].text?.text}</span>
    <!-- <span>x:{Math.round(position.x)},y:{Math.round(position.y)}</span> -->
  </NodeContent>
  <OutputAnchor bind:nextBlockId={config.next_block_id} />
</Node>
