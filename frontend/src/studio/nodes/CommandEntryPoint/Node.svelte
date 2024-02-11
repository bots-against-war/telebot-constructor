<script lang="ts">
  import { Node } from "svelvet";
  import type { CommandEntryPoint } from "../../../api/types";
  import type { SvelvetPosition } from "../../../types";
  import { getModalOpener } from "../../../utils";
  import InputAnchor from "../../components/InputAnchor.svelte";
  import NodeContent from "../../components/NodeContent.svelte";
  import OutputAnchor from "../../components/OutputAnchor.svelte";
  import OutputAnchorsBox from "../../components/OutputAnchorsBox.svelte";
  import { NodeTypeKey } from "../display";
  import { DEFAULT_NODE_PROPS } from "../nodeProps";
  import Modal from "./Modal.svelte";

  const openModal = getModalOpener<Modal>();

  export let config: CommandEntryPoint;
  export let position: SvelvetPosition;
  export let isValid = true;

  let isStart = config.command === "start";
</script>

<Node id={config.entrypoint_id} bind:position {...DEFAULT_NODE_PROPS}>
  {#if isStart}
    <InputAnchor dummy />
  {/if}
  <NodeContent
    key={NodeTypeKey.command}
    deletable={!isStart}
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
    <span class="font-mono font-bold">/{config.command}</span>
  </NodeContent>
  <OutputAnchorsBox>
    <OutputAnchor bind:nextBlockId={config.next_block_id} />
  </OutputAnchorsBox>
</Node>
