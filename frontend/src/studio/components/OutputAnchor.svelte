<script lang="ts">
  import { Anchor } from "svelvet";
  import type { SvelvetConnection } from "../../types";
  import DeletableEdge from "./DeletableEdge.svelte";
  export let connection: SvelvetConnection;
</script>

<div class="anchor-container">
  <Anchor direction="south" multiple={false} output connections={[connection]} edge={DeletableEdge} />
</div>

<style>
  div.anchor-container {
    width: 100%;
    display: flex;
    flex-direction: row;
    justify-content: center;
  }
</style>
