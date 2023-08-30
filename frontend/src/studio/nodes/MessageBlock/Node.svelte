<script lang="ts">
  import { Node } from "svelvet";
  import type { MessageBlock } from "../../../api/types";
  import NodeContent from "../../layout/NodeContent.svelte";
  import OutputAnchor from "../../layout/OutputAnchor.svelte";
  import InputAnchor from "../../layout/InputAnchor.svelte";
  import type { SvelvetPosition } from "../../../types";

  import Modal from "./Modal.svelte";
  import { getModalOpener } from "../../../utils";
  const openModal = getModalOpener();

  export let config: MessageBlock;
  export let position: SvelvetPosition;
</script>

<Node id={config.block_id} bgColor="#bfebff" bind:position on:nodeReleased>
  <InputAnchor />
  <NodeContent
    name="Message"
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
  <OutputAnchor connection={config.next_block_id} />
</Node>
