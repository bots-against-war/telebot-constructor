<script>
  import { createEventDispatcher } from "svelte";
  import { Edge } from "svelvet";

  const dispatch = createEventDispatcher();
</script>

<Edge let:path let:destroy>
  <path d={path} />
  <button
    slot="label"
    on:click={(e) => {
      dispatch("deleted");
      destroy();
    }}>⨯</button
  >
</Edge>

<style>
  path {
    stroke: grey;
    stroke-width: 3px;
  }

  button {
    background-color: rgb(189, 189, 189);
    padding: 0.5em;
    margin: 0;
    border: 1px grey solid;
    border-radius: 100%;
    aspect-ratio: 1 / 1;
    cursor: pointer;
  }
</style>
