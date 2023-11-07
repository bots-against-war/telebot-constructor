<script lang="ts">
  import { Anchor, type Connections } from "svelvet";
  import { svelvetNodeIdToBlockId } from "../utils";
  import DummyEdge from "./DummyEdge.svelte";

  export let nextBlockId: string | null | undefined;
  export let anchorLabel: string | null = null;
  export let dummy: boolean = false;

  nextBlockId = nextBlockId === undefined ? null : nextBlockId;

  let initialConnections: Connections = nextBlockId ? [nextBlockId] : [];
</script>

<div class="anchor-and-label" class:dummy>
  <Anchor
    direction="south"
    multiple={false}
    edge={dummy ? DummyEdge : null}
    locked={dummy}
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
    top: -8px;
    --anchor-width: 16px;
    --anchor-height: 16px;
  }
  div.dummy {
    top: -3px;
    --anchor-width: 6px;
    --anchor-height: 6px;
  }

  div.floating-anchor-name {
    color: white;
    background-color: var(--prop-anchor-color, var(--anchor-color, var(--default-anchor-color)));
    padding: 0 5px;
    border-radius: 5px;
    max-width: 60px;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  div.linked {
    background-color: var(--anchor-connected, var(--default-anchor-connected));
  }
</style>
