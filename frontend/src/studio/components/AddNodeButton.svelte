<script lang="ts">
  import {
    NODE_HUE as NODE_HUE,
    NODE_ICON as NODE_ICON,
    NodeTypeKey,
    NODE_TITLE as NODE_TITLE,
    headerColor,
  } from "../nodes/display";

  export let key: NodeTypeKey;

  $: hue = NODE_HUE[key];
  $: title = NODE_TITLE[key];
  $: icon = NODE_ICON[key];
</script>

<button on:click class="add-node-button">
  <div class="icon-container" style={`background-color: ${headerColor(hue)}`}>
    <svelte:component this={icon} />
  </div>
  <span class="title">
    {title}
  </span>
</button>

<style>
  button.add-node-button {
    background-color: initial;
    border: 1px solid rgb(6, 89, 122);
    border-radius: 10px;
    display: flex;
    align-items: center;
    width: 100%;
    padding: 0;
    cursor: pointer;
  }
  div.icon-container {
    width: 20px;
    height: 20px;
    display: flex;
    justify-items: center;
    align-items: center;
    padding: 6px;
    border-radius: 9px 0 0 9px;
    border-right: 1px solid rgb(6, 89, 122);
  }
  span.title {
    padding: 6px;
    font-size: large;
  }
</style>
