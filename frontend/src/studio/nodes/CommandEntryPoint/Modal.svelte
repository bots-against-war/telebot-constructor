<script lang="ts">
  import { TextInput } from "@svelteuidev/core";
  import { BarsSolid } from "flowbite-svelte-icons";
  import NodeModalControls from "../../components/NodeModalControls.svelte";

  import type { CommandEntryPoint } from "../../../api/types";

  import { NODE_TITLE } from "../display";
  import SlashIcon from "./SlashIcon.svelte";

  export let config: CommandEntryPoint;
  export let onConfigUpdate: (newConfig: CommandEntryPoint) => any;

  function updateConfig() {
    onConfigUpdate(editedConfig);
  }

  let editedConfig: CommandEntryPoint = JSON.parse(JSON.stringify(config));
  let isStartCmd = config.command === "start"; // non-reactive, on start only
</script>

<div>
  <h3>{NODE_TITLE.command}</h3>
  <TextInput
    bind:value={editedConfig.command}
    disabled={isStartCmd}
    error={!isStartCmd && editedConfig.command === "start" ? "Зарезервированная команда" : null}
  >
    <SlashIcon slot="icon" width={10} />
  </TextInput>
  <NodeModalControls on:save={updateConfig} />
</div>
