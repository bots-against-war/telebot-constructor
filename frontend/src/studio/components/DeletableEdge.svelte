<script>
  import { CloseOutline } from "flowbite-svelte-icons";
  import { Edge } from "svelvet";
</script>

<Edge let:path>
  <path d={path} />
  <button class="close-button" slot="label" let:destroy on:click={destroy}>
    <CloseOutline size="md" color="white" class="p-0" />
  </button>
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
