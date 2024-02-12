<script lang="ts">
  import type { ContentBlock } from "../../../api/types";
  import LocalizableTextInput from "../../components/LocalizableTextInput.svelte";
  import NodeModalBody from "../../components/NodeModalBody.svelte";
  import NodeModalControls from "../../components/NodeModalControls.svelte";
  import { NODE_TITLE } from "../display";

  export let config: ContentBlock;
  export let onConfigUpdate: (newConfig: ContentBlock) => any;

  function updateConfig() {
    config.contents = [{ text: { text: editedMessageText, markup: "none" }, attachments: [] }];
    onConfigUpdate(config);
  }

  let editedMessageText = config.contents[0].text?.text || "";
</script>

<NodeModalBody title={NODE_TITLE.content}>
  <LocalizableTextInput label="Текст сообщения" bind:value={editedMessageText} />
  <NodeModalControls on:save={updateConfig} />
</NodeModalBody>

<style>
</style>
