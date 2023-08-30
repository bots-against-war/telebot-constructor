<script lang="ts">
  export let name: string;
</script>

<div class="node-content">
  <h3>{name}</h3>
  <slot />
</div>

<style>
  div.node-content {
    width: fit-content;
    height: 100%;
    display: flex;
    flex-flow: column;
    padding: 1em;
  }

  h3 {
    margin: 0.3em 0;
  }
</style>
