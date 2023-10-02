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

  const setNewConfig = (newConfig: HumanOperatorBlock) => {
    config = newConfig;
  };
</script>

<Node id={config.block_id} bgColor="#b2db81" bind:position>
  <InputAnchor />
  <NodeContent
    name="Человек-оператор"
    on:delete
    on:edit={() =>
      openModal(Modal, {
        config,
        onConfigUpdate: setNewConfig,
      })}
  >
    <span>TBD</span>
    <!-- <span>x:{Math.round(position.x)},y:{Math.round(position.y)}</span> -->
  </NodeContent>
</Node>
