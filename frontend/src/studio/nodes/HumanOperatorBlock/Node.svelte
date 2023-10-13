<script lang="ts">
  import { getContext } from "svelte";

  import { Node } from "svelvet";

  import type { SvelvetPosition } from "../../../types";
  import type { HumanOperatorBlock } from "../../../api/types";
  import { getModalOpener } from "../../../utils";

  import Modal from "./Modal.svelte";
  import GroupChatBadge from "../../../components/GroupChatBadge.svelte";
  import NodeContent from "../../components/NodeContent.svelte";
  import InputAnchor from "../../components/InputAnchor.svelte";
  import { PLACEHOLDER_GROUP_CHAT_ID } from "../defaultConfigs";
  import { DEFAULT_NODE_PROPS } from "../nodeProps";
  import ErrorBadge from "../../../components/ErrorBadge.svelte";
  import { HUE, headerColor } from "../colors";

  const openModal = getModalOpener();

  export let config: HumanOperatorBlock;
  export let position: SvelvetPosition;

  const botName: string = getContext("botName");

  const setNewConfig = (newConfig: HumanOperatorBlock) => {
    config = newConfig;
    console.log(config);
  };

  function openEditModal() {
    openModal(Modal, {
      config,
      botName,
      onConfigUpdate: setNewConfig,
    });
  }

  if (config.feedback_handler_config.admin_chat_id === PLACEHOLDER_GROUP_CHAT_ID) {
    openEditModal();
  }
</script>

<Node id={config.block_id} bind:position {...DEFAULT_NODE_PROPS}>
  <InputAnchor />
  <NodeContent name="Человек-оператор" headerColor={headerColor(HUE.human_operator)} on:delete on:edit={openEditModal}>
    {#if config.feedback_handler_config.admin_chat_id === PLACEHOLDER_GROUP_CHAT_ID}
      <ErrorBadge text="Не выбран админ-чат" />
    {:else}
      <GroupChatBadge {botName} chatId={config.feedback_handler_config.admin_chat_id} />
    {/if}
  </NodeContent>
</Node>
