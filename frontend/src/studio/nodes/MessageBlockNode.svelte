<script lang="ts">
  import { Anchor, Node } from "svelvet";
  import type { MessageBlock } from "../../api/types";
  import NodeContent from "../layout/NodeContent.svelte";
  import OutputAnchor from "../layout/OutputAnchor.svelte";
  import InputAnchor from "../layout/InputAnchor.svelte";

  export let config: MessageBlock;
</script>

<Node id={config.block_id} bgColor="#bfebff">
  <InputAnchor />
  <NodeContent name="Message">
    <span>{config.message_text}</span>
  </NodeContent>
  <OutputAnchor connection={config.next_block_id} />
</Node>
