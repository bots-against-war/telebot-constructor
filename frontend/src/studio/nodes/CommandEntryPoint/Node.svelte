<script lang="ts">
  import { Node } from "svelvet";
  import Modal from "./Modal.svelte";
  import NodeContent from "../../components/NodeContent.svelte";
  import OutputAnchorsBox from "../../components/OutputAnchorsBox.svelte";
  import OutputAnchor from "../../components/OutputAnchor.svelte";

  import type { CommandEntryPoint } from "../../../api/types";
  import type { SvelvetPosition } from "../../../types";

  import { getModalOpener } from "../../../utils";
  import { DEFAULT_NODE_PROPS } from "../nodeProps";
  import { NodeTypeKey } from "../display";
  const openModal = getModalOpener<Modal>();

  export let config: CommandEntryPoint;
  export let position: SvelvetPosition;
  export let isValid = true;
</script>

<Node id={config.entrypoint_id} bind:position {...DEFAULT_NODE_PROPS}>
  <NodeContent
    key={NodeTypeKey.command}
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
  <OutputAnchorsBox>
    <OutputAnchor bind:nextBlockId={config.next_block_id} />
  </OutputAnchorsBox>
</Node>
