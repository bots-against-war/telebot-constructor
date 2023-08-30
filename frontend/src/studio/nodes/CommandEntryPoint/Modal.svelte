<script lang="ts">
  import type { CommandEntryPoint } from "../../../api/types";
  import { getModalCloser } from "../../../utils";

  const closeModal = getModalCloser();

  export let config: CommandEntryPoint;
  export let onConfigUpdate: (CommandEntryPoint) => any;

  function updateConfig() {
    config.command = editedCommand;
    onConfigUpdate(config);
    closeModal();
  }

  let editedCommand = config.command;
</script>

<div>
  <h3>Command entry point</h3>
  /<input bind:value={editedCommand} />
  <div class="buttons-row">
    <button on:click={updateConfig}>OK</button>
    <button on:click={closeModal}>Cancel</button>
  </div>
</div>

<style>
  div.buttons-row {
    margin-top: 1em;
    width: 100%;
    display: flex;
    flex-direction: row;
    justify-content: space-around;
  }
</style>
