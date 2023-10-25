<script lang="ts">
  import { Tabs } from "@svelteuidev/core";
  import type { FormBlock } from "../../../api/types";
  import NodeModalControls from "../../components/NodeModalControls.svelte";

  import FormBranch from "./components/FormBranch.svelte";
  import FormMessages from "./components/FormMessages.svelte";

  export let config: FormBlock;
  export let onConfigUpdate: (newConfig: FormBlock) => any;

  function updateConfig() {
    config = editedConfig;
    onConfigUpdate(config);
  }

  let editedConfig: FormBlock = JSON.parse(JSON.stringify(config));
</script>

<div>
  <h3>Форма</h3>
  <Tabs>
    <Tabs.Tab label={`Поля (${editedConfig.members.length})`}>
      <FormBranch bind:members={editedConfig.members} />
    </Tabs.Tab>
    <Tabs.Tab label="Сообщения">
      <FormMessages bind:messages={editedConfig.messages} />
    </Tabs.Tab>
  </Tabs>
  <NodeModalControls on:save={updateConfig} />
</div>

<style>
</style>
