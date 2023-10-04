<script lang="ts">
  import type { HumanOperatorBlock } from "../../../api/types";
  import NodeModalControls from "../../components/NodeModalControls.svelte";
  import GroupChatIdSelect from "../../components/GroupChatIdSelect.svelte";

  export let botName: string; //required for admin chat id rendering, and context does not propagate here
  export let config: HumanOperatorBlock;
  export let onConfigUpdate: (newConfig: HumanOperatorBlock) => any;

  function updateConfig() {
    config.feedback_handler_config.admin_chat_id = adminChatId;
    onConfigUpdate(config);
  }

  let adminChatId = config.feedback_handler_config.admin_chat_id;
</script>

<div>
  <h3>Человек-оператор</h3>
  <div>
    <GroupChatIdSelect label="Админ-чат" {botName} bind:selectedGroupChatId={adminChatId} />
  </div>
  <NodeModalControls on:save={updateConfig} />
</div>
