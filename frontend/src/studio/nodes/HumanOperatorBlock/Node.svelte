<script lang="ts">
  import { Node } from "svelvet";
  import type { HumanOperatorBlock } from "../../../api/types";
  import NodeContent from "../../components/NodeContent.svelte";
  import InputAnchor from "../../components/InputAnchor.svelte";
  import type { SvelvetPosition } from "../../../types";

  import Modal from "./Modal.svelte";
  import { getModalOpener } from "../../../utils";
  const openModal = getModalOpener();

  export let config: HumanOperatorBlock;
  export let position: SvelvetPosition;
</script>

<Node id={config.block_id} bgColor="#b2db81" bind:position>
  <InputAnchor />
  <NodeContent
    name="Human operator"
    on:delete
    on:edit={() =>
      openModal(Modal, {
        config,
        onConfigUpdate: (newConfig) => {
          config = newConfig;
        },
      })}
  >
    <span>TBD</span>
    <!-- <span>x:{Math.round(position.x)},y:{Math.round(position.y)}</span> -->
  </NodeContent>
</Node>
