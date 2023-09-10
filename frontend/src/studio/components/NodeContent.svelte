<script lang="ts">
  import { createEventDispatcher } from "svelte";

  export let name: string;

  const dispatch = createEventDispatcher();
</script>

<div class="node-content">
  <h3>{name}</h3>
  <slot />
  <div class="controls">
    <button on:click={(e) => dispatch("edit")}>Edit</button>
    <button on:click={(e) => dispatch("delete")}>Delete</button>
  </div>
</div>

<style>
  div.node-content {
    display: flex;
    flex-flow: column;
    margin: 0.4em 0.8em;
  }

  h3 {
    margin: 0.2em 0;
  }

  div.controls {
    width: 100%;
    display: flex;
    justify-content: center;
    margin: 0.4em 0;
  }
</style>
