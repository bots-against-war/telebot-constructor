<script lang="ts">
  import { Node } from "svelvet";
  import type { CommandEntryPoint } from "../../../api/types";
  import NodeContent from "../../components/NodeContent.svelte";
  import OutputAnchor from "../../components/OutputAnchor.svelte";
  import type { SvelvetPosition } from "../../../types";

  import Modal from "./Modal.svelte";
  import { getModalOpener } from "../../../utils";
  import { DEFAULT_NODE_PROPS } from "../nodeProps";
  import { HUE, headerColor } from "../colors";
  const openModal = getModalOpener<Modal>();

  export let config: CommandEntryPoint;
  export let position: SvelvetPosition;
  export let isValid = true;
</script>

<Node id={config.entrypoint_id} bind:position {...DEFAULT_NODE_PROPS}>
  <NodeContent
    name="Команда"
    headerColor={headerColor(HUE.command)}
    bind:isValid
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
  </NodeContent>
  <OutputAnchor bind:nextBlockId={config.next_block_id} />
</Node>
