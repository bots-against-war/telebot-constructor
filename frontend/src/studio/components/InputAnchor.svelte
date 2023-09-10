<script lang="ts">
  import { Anchor } from "svelvet";
  import DeletableEdge from "./DeletableEdge.svelte";
</script>

<div class="anchor-container">
  <Anchor direction="north" multiple input />
</div>

<style>
  div.anchor-container {
    width: 100%;
    display: flex;
    flex-direction: row;
    justify-content: center;
  }
</style>
