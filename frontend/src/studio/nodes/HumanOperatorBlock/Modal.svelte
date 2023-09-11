<script lang="ts">
  import type { HumanOperatorBlock } from "../../../api/types";
  import { getModalCloser } from "../../../utils";

  const closeModal = getModalCloser();

  export let config: HumanOperatorBlock;
  export let onConfigUpdate: (HumanOperatorBlock) => any;

  function updateConfig() {
    config.feedback_handler_config.admin_chat_id = adminChatId;
    onConfigUpdate(config);
    closeModal();
  }

  let adminChatId = config.feedback_handler_config.admin_chat_id;
</script>

<div>
  <h3>Human operator via bot</h3>
  <span>
    <b>Admin chat id:</b>
    <input bind:value={adminChatId} type="number" />
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
