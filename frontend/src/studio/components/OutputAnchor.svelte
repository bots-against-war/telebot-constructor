<script lang="ts">
  import { Anchor, type Connections } from "svelvet";
  import { svelvetNodeIdToBlockId } from "../utils";

  export let nextBlockId: string | null;
  export let anchorLabel: string | null = null;

  let initialConnections: Connections = nextBlockId !== null ? [nextBlockId] : [];
</script>

<div class="anchor-and-label">
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
  {#if anchorLabel !== null}
    <div class="floating-anchor-name" class:linked={nextBlockId !== null}>{anchorLabel}</div>
  {/if}
</div>

<style>
  div.anchor-and-label {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 3px;
    position: relative;
    top: -6px;
  }

  div.floating-anchor-name {
    color: white;
    background-color: var(--prop-anchor-color, var(--anchor-color, var(--default-anchor-color)));
    padding: 0 5px;
    border-radius: 5px;
  }

  div.linked {
    background-color: var(--anchor-connected, var(--default-anchor-connected));
  }
</style>
