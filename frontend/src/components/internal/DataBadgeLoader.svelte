<!-- Loader to be used inside DataBadge -->
<script lang="ts">
  import { Loader } from "@svelteuidev/core";
</script>

<div class="container">
  <Loader size="sm" />
</div>

<style>
  div.container {
    width: 100%;
    height: 1em;
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
  }
</style>
