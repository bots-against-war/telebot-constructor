<div class="custom-controls">
  <slot />
</div>

<style>
  div.custom-controls {
    position: fixed;
    top: 60px; /* TODO: unhardcode header height */
    left: 10px;
    border-radius: 15px;
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
