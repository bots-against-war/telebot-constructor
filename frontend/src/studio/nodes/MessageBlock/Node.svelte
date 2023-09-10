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
</script>

<Node id={config.block_id} bgColor="#bfebff" bind:position>
  <InputAnchor />
  <NodeContent
    name="Message"
    on:delete
    on:edit={() =>
      openModal(Modal, {
        config,
        onConfigUpdate: (newConfig) => {
          config = newConfig;
        },
      })}
  >
    <span>{config.message_text}</span>
  </NodeContent>
  <OutputAnchor bind:nextBlockId={config.next_block_id} />
</Node>
