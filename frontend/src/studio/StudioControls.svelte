<script lang="ts">
  export let title: string | null = null;
  export let position: "upper-left" | "upper-right" | "lower-right";

  let style: string = "";
  if (position === "upper-left") style = "left: 10px; top: 10px;";
  else if (position === "upper-right") style = "right: 10px; top: 10px;";
  else if (position === "lower-right") style = "right: 10px; bottom: 10px;";

  if (title !== null) style = style.concat("padding-top: 4px;");
</script>

<div class="custom-controls" {style}>
  {#if title !== null}
    <h3>{title}</h3>
  {/if}
  <slot />
</div>

<style>
  div.custom-controls {
    position: fixed;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-around;
    /* copied from svelvet controls css */
    box-shadow: var(--controls-shadow, var(--default-controls-shadow));
    border: solid 1px var(--controls-border, var(--default-controls-border));
    padding: 10px;
    color: var(--prop-controls-text-color, var(--controls-text-color, var(--default-controls-text-color)));
    background-color: var(
      --prop-controls-background-color,
      var(--controls-background-color, var(--default-controls-background-color))
    );
  }
  div.custom-controls > h3 {
    margin: 0.2em 0.5em;
    text-align: center;
    width: 100%;
  }
</style>
