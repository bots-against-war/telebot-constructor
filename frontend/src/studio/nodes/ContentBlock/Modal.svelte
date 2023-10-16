<script lang="ts">
  import { Stack } from "@svelteuidev/core";
  import type { ContentBlock } from "../../../api/types";
  import NodeModalControls from "../../components/NodeModalControls.svelte";
  import LocalizableTextInput from "../../components/LocalizableTextInput.svelte";

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
  <Stack>
    <LocalizableTextInput label="Текст сообщения" bind:value={editedMessageText} />
  </Stack>
  <NodeModalControls on:save={updateConfig} />
</div>

<style>
</style>
