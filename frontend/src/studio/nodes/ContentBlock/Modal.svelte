<script lang="ts">
  import type { ContentBlock } from "../../../api/types";
  import NodeModalControls from "../../components/NodeModalControls.svelte";

  export let config: ContentBlock;
  export let onConfigUpdate: (newConfig: ContentBlock) => any;

  function updateConfig() {
    config.contents = [{ text: { text: editedMessageText, markup: "none" }, attachments: [] }];
    onConfigUpdate(config);
  }

  let editedMessageText = config.contents[0].text?.text || "";
</script>

<div>
  <h3>Контент</h3>
  <span>
    <b>Текст сообщения:</b>
    <input bind:value={editedMessageText} />
  </span>

  <NodeModalControls on:save={updateConfig} />
</div>

<style>
</style>
