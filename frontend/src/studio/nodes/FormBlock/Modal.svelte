<script lang="ts">
  import { Stack } from "@svelteuidev/core";
  import type { FormBlock } from "../../../api/types";
  import NodeModalControls from "../../components/NodeModalControls.svelte";

  import FormBranch from "./components/FormBranch.svelte";

  export let config: FormBlock;
  export let onConfigUpdate: (newConfig: FormBlock) => any;

  function updateConfig() {
    // config.contents = [{ text: { text: editedMessageText, markup: "none" }, attachments: [] }];
    onConfigUpdate(config);
  }

  let editedConfig: FormBlock = JSON.parse(JSON.stringify(config));
</script>

<div>
  <h3>Форма</h3>
  <Stack>
    <FormBranch bind:members={editedConfig.members} />
  </Stack>
  <NodeModalControls on:save={updateConfig} />
</div>

<style>
</style>
