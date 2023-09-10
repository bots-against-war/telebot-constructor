<script>
  import { Edge } from "svelvet";
</script>

<Edge let:path edgeClick={() => console.log("Edge clicked")} let:destroy enableHover let:hovering>
  <path d={path} class:hovering />
  <button
    slot="label"
    on:click={(e) => {
      console.log(`Destroy clicked: ${e}`);
      destroy();
    }}
  >
    XXX
  </button>
</Edge>

<style>
  path {
    stroke: grey;
    stroke-width: 3px;
  }

  path.hovering {
    stroke: red;
    stroke-width: 8px;
    cursor: crosshair;
  }
</style>
