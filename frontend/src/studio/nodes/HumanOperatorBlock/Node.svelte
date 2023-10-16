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
  import { DEFAULT_NODE_PROPS } from "../nodeProps";
  import { HUE, headerColor } from "../colors";
  import { validateHumanOperatorBlock } from "../nodeValidators";

  const openModal = getModalOpener();

  export let config: HumanOperatorBlock;
  export let position: SvelvetPosition;
  export let isValid = true;

  const botName: string = getContext("botName");

  const setNewConfig = (newConfig: HumanOperatorBlock) => {
    config = newConfig;
  };

  function openEditModal() {
    openModal(Modal, {
      config,
      botName,
      onConfigUpdate: setNewConfig,
    });
  }
</script>

<Node id={config.block_id} bind:position {...DEFAULT_NODE_PROPS}>
  <InputAnchor />
  <NodeContent
    name="Человек-оператор"
    headerColor={headerColor(HUE.human_operator)}
    bind:isValid
    {config}
    configValidator={validateHumanOperatorBlock}
    on:delete
    on:edit={openEditModal}
  >
    <GroupChatBadge {botName} chatId={config.feedback_handler_config.admin_chat_id} />
  </NodeContent>
</Node>
