<script lang="ts">
  import type { LanguageSelectBlock } from "../../../api/types";
  import NodeModalControls from "../../components/NodeModalControls.svelte";

  export let config: LanguageSelectBlock;
  export let onConfigUpdate: (newConfig: LanguageSelectBlock) => any;

  function updateConfig() {
    onConfigUpdate(config);
  }
</script>

<div>
  <h3>Выбор языка</h3>
  <NodeModalControls on:save={updateConfig} />
</div>
