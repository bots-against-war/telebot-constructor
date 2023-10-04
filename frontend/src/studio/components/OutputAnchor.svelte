<script lang="ts">
  import { Anchor, type Connections } from "svelvet";
  import { svelvetNodeIdToBlockId } from "../utils";

  export let nextBlockId: string | null;

  let initialConnections: Connections = nextBlockId !== null ? [nextBlockId] : [];
</script>

<div class="anchor-container">
  <Anchor
    direction="south"
    multiple={false}
    output
    connections={initialConnections}
    on:connection={(e) => {
      const connectedNode = e.detail.connectedNode;
      nextBlockId = svelvetNodeIdToBlockId(connectedNode.id);
    }}
    on:disconnection={(e) => {
      nextBlockId = null;
    }}
  />
</div>

<style>
  div.anchor-container {
    width: 100%;
    display: flex;
    flex-direction: row;
    justify-content: center;
    height: 6px;
  }
</style>
