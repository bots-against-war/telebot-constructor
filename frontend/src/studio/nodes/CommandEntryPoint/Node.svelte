<script lang="ts">
  import { Node } from "svelvet";
  import type { CommandEntryPoint } from "../../../api/types";
  import NodeContent from "../../components/NodeContent.svelte";
  import OutputAnchor from "../../components/OutputAnchor.svelte";
  import type { SvelvetPosition } from "../../../types";

  import Modal from "./Modal.svelte";
  import { getModalOpener } from "../../../utils";
  const openModal = getModalOpener<Modal>();

  export let config: CommandEntryPoint;
  export let position: SvelvetPosition;
</script>

<Node id={config.entrypoint_id} bgColor="#f9d6a7" bind:position>
  <NodeContent
    name="Command"
    on:delete
    on:edit={() =>
      openModal(Modal, {
        config,
        onConfigUpdate: (newConfig) => {
          config = newConfig;
        },
      })}
  >
    <span>/{config.command}</span>
    <!-- <span>x:{Math.round(position.x)},y:{Math.round(position.y)}</span> -->
  </NodeContent>
  <OutputAnchor bind:nextBlockId={config.next_block_id} />
</Node>
