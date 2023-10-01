<script lang="ts">
  import type { ContentBlock } from "../../../api/types";
  import { getModalCloser } from "../../../utils";

  const closeModal = getModalCloser();

  export let config: ContentBlock;
  export let onConfigUpdate: (newConfig: ContentBlock) => any;

  function updateConfig() {
    config.contents = [{ text: { text: editedMessageText, markup: "none" }, attachments: [] }];
    onConfigUpdate(config);
    closeModal();
  }

  let editedMessageText = config.contents[0].text?.text || "";
</script>

<div>
  <h3>Content</h3>
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
