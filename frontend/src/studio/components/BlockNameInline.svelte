<script lang="ts">
  import { headerColor, NODE_HUE, NODE_TITLE, NodeTypeKey } from "../nodes/display";

  export let key: NodeTypeKey;
</script>

<strong class="px-0.5 py-0.25 rounded-none" style="background-color: {headerColor(NODE_HUE[key])}"
  >{NODE_TITLE[key]}</strong
>
