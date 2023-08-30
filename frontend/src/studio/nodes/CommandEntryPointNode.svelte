<script lang="ts">
  import { Anchor, Node } from "svelvet";
  import type { CommandEntryPoint } from "../../api/types";
  import NodeContent from "../layout/NodeContent.svelte";
  import OutputAnchor from "../layout/OutputAnchor.svelte";

  export let config: CommandEntryPoint;
</script>

<Node id={config.entrypoint_id} bgColor="#f9d6a7">
  <NodeContent name="Command">
    <span>/{config.command}</span>
  </NodeContent>
  <OutputAnchor connection={config.next_block_id} />
</Node>
