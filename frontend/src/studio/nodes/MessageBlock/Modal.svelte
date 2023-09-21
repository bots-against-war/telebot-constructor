<script lang="ts">
  import type { MessageBlock } from "../../../api/types";
  import { getModalCloser } from "../../../utils";

  const closeModal = getModalCloser();

  export let config: MessageBlock;
  export let onConfigUpdate: (newConfig: MessageBlock) => any;

  function updateConfig() {
    config.message_text = editedMessageText;
    onConfigUpdate(config);
    closeModal();
  }

  let editedMessageText = config.message_text;
</script>

<div>
  <h3>Simple bot->user message</h3>
  <span>
    <b>Message text:</b>
    <input bind:value={editedMessageText} />
  </span>
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
