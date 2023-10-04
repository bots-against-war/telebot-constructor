<script lang="ts">
  import { getContext } from "svelte";

  import { Node } from "svelvet";
  import { Alert } from "@svelteuidev/core";

  import type { SvelvetPosition } from "../../../types";
  import type { HumanOperatorBlock } from "../../../api/types";
  import { getModalOpener } from "../../../utils";

  import Modal from "./Modal.svelte";
  import GroupChatBadge from "../../../components/GroupChatBadge.svelte";
  import NodeContent from "../../components/NodeContent.svelte";
  import InputAnchor from "../../components/InputAnchor.svelte";
  import { PLACEHOLDER_GROUP_CHAT_ID } from "../defaultConfigs";
  import { ExclamationTriangle } from "radix-icons-svelte";
  import { DEFAULT_NODE_PROPS } from "../nodeProps";

  const openModal = getModalOpener();

  export let config: HumanOperatorBlock;
  export let position: SvelvetPosition;

  const botName: string = getContext("botName");

  const setNewConfig = (newConfig: HumanOperatorBlock) => {
    config = newConfig;
    console.log("HO config updated");
    console.log(config);
  };
</script>

<Node id={config.block_id} bind:position {...DEFAULT_NODE_PROPS}>
  <InputAnchor />
  <NodeContent
    name="Человек-оператор"
    headerColor="#b1d162"
    on:delete
    on:edit={() =>
      openModal(Modal, {
        config,
        botName,
        onConfigUpdate: setNewConfig,
      })}
  >
    {#if config.feedback_handler_config.admin_chat_id === PLACEHOLDER_GROUP_CHAT_ID}
      <div>
        <Alert color="red" icon={ExclamationTriangle}>Не выбран админ-чат</Alert>
      </div>
    {:else}
      <GroupChatBadge {botName} chatId={config.feedback_handler_config.admin_chat_id} />
    {/if}
  </NodeContent>
</Node>
