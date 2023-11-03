<script>
  import { Edge } from "svelvet";
</script>

<Edge let:path>
  <path d={path} />
</Edge>

<style>
  path {
    stroke: var(--anchor-connected, var(--default-anchor-connected));
    stroke-width: 2px;
    stroke-dasharray: 5;
  }
</style>
