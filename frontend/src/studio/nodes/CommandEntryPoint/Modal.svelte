<script lang="ts">
  import type { CommandEntryPoint } from "../../../api/types";
  import NodeModalControls from "../../components/NodeModalControls.svelte";

  export let config: CommandEntryPoint;
  export let onConfigUpdate: (newConfig: CommandEntryPoint) => any;

  function updateConfig() {
    config.command = editedCommand;
    onConfigUpdate(config);
  }

  let editedCommand = config.command;
</script>

<div>
  <h3>Команда</h3>
  /<input bind:value={editedCommand} />
  <NodeModalControls on:save={updateConfig} />
</div>
