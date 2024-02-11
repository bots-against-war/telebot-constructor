<script lang="ts">
  import { NODE_HUE, NODE_ICON, NODE_TITLE, NodeTypeKey, headerColor } from "../nodes/display";

  export let key: NodeTypeKey;

  $: hue = NODE_HUE[key];
  $: title = NODE_TITLE[key];
  $: icon = NODE_ICON[key];
</script>

<button on:click class="border border-gray-500 flex flex-row items-center justify-start p-0 rounded-lg w-auto">
  <div class="w-10 h-10 flex justify-center items-center rounded-s-lg" style={`background-color: ${headerColor(hue)}`}>
    <svelte:component this={icon} class="w-7 h-7" />
  </div>
  <span class="font-bold px-3">
    {title}
  </span>
</button>
