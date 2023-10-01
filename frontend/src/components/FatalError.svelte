<script lang="ts">
  import Centered from "./Centered.svelte";

  export let error: any;
  console.log("Fatal error catched: ", error);
</script>

<Centered>
  <h2 class="error">{error}</h2>
</Centered>

<style>
  h2.error {
    color: #ec6969;
  }
</style>
