<script lang="ts">
  import bawLogo from "/baw.svg";
  import BaseConstructor from "./BaseConstructor.svelte";
</script>

<main>
  <div>
    <img src={bawLogo} class="logo" alt="BAW Logo" />
  </div>
  <div class="constructor">
    <BaseConstructor />
  </div>
</main>

<style>
  .logo {
    height: 6em;
    padding: 1.5em;
    will-change: filter;
    transition: filter 300ms;
  }
  .logo:hover {
    filter: drop-shadow(0 0 2em #646cffaa);
  }
</style>
