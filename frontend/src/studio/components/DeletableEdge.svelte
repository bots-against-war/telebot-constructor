<script>
  import { Edge } from "svelvet";

  import { CloseIcon } from "@svelteuidev/core";
</script>

<Edge let:path>
  <path d={path} />
  <button class="close-button" slot="label" let:destroy on:click={destroy}
    ><CloseIcon size="xs" color="white" style="stoke: white;" /></button
  >
</Edge>

<style>
  path {
    stroke: var(--anchor-connected, var(--default-anchor-connected));
    stroke-width: 3px;
  }

  button.close-button {
    background-color: var(--anchor-connected, var(--default-anchor-connected));
    padding: 1px;
    border: 1px var(--anchor-connected, var(--default-anchor-connected)) solid;
    border-radius: 100%;
    cursor: pointer;
    display: flex;
  }
</style>
