<script lang="ts">
  import { Button } from "flowbite-svelte";
  import { NODE_HUE, NODE_ICON, NODE_TITLE, NodeTypeKey, headerColor } from "../nodes/display";

  export let key: NodeTypeKey;
  export let disabled: boolean = false;

  $: hue = NODE_HUE[key];
  $: title = NODE_TITLE[key];
  $: icon = NODE_ICON[key];
</script>

<Button
  on:click
  outline
  class="border border-gray-500 flex flex-row items-center justify-start p-0 rounded-lg w-auto hover:bg-inherit hover:text-inherit"
  {disabled}
>
  <div class="w-10 h-10 flex justify-center items-center rounded-s-lg" style={`background-color: ${headerColor(hue)}`}>
    <svelte:component this={icon} class="w-7 h-7" />
  </div>
  <span class="font-bold px-3">
    {title}
  </span>
</Button>
