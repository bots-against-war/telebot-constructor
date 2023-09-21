<script lang="ts">
  import { Node } from "svelvet";
  import type { MessageBlock } from "../../../api/types";
  import NodeContent from "../../components/NodeContent.svelte";
  import OutputAnchor from "../../components/OutputAnchor.svelte";
  import InputAnchor from "../../components/InputAnchor.svelte";
  import type { SvelvetPosition } from "../../../types";

  import Modal from "./Modal.svelte";
  import { getModalOpener } from "../../../utils";
  const openModal = getModalOpener();

  export let config: MessageBlock;
  export let position: SvelvetPosition;
  const setNewConfig = (newConfig: MessageBlock) => {
    config = newConfig;
  };
</script>

<Node id={config.block_id} bgColor="#bfebff" bind:position>
  <InputAnchor />
  <NodeContent
    name="Message"
    on:delete
    on:edit={() =>
      openModal(Modal, {
        config,
        onConfigUpdate: setNewConfig,
      })}
  >
    <span>{config.message_text}</span>
    <!-- <span>x:{Math.round(position.x)},y:{Math.round(position.y)}</span> -->
  </NodeContent>
  <OutputAnchor bind:nextBlockId={config.next_block_id} />
</Node>
