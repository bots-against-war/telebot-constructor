<script lang="ts">
  import { getContext } from "svelte";

  import { Node } from "svelvet";
  import { Alert } from "@svelteuidev/core";

  import type { SvelvetPosition } from "../../../types";
  import type { HumanOperatorBlock } from "../../../api/types";
  import { getModalOpener } from "../../../utils";

  import Modal from "./Modal.svelte";
  import GroupChat from "../../../components/GroupChat.svelte";
  import NodeContent from "../../components/NodeContent.svelte";
  import InputAnchor from "../../components/InputAnchor.svelte";
  import { PLACEHOLDER_GROUP_CHAT_ID } from "../defaultConfigs";

  const openModal = getModalOpener();

  export let config: HumanOperatorBlock;
  export let position: SvelvetPosition;

  const botName: string = getContext("botName");

  const setNewConfig = (newConfig: HumanOperatorBlock) => {
    config = newConfig;
  };
</script>

<Node id={config.block_id} bgColor="#b2db81" bind:position>
  <InputAnchor />
  <NodeContent
    name="Человек-оператор"
    on:delete
    on:edit={() =>
      openModal(Modal, {
        config,
        onConfigUpdate: setNewConfig,
      })}
  >
    <!-- <span style="background-color: red;">TEST 1312</span> -->
    {#if config.feedback_handler_config.admin_chat_id === PLACEHOLDER_GROUP_CHAT_ID}
      <div>
        <!-- TODO: warning icon -->
        <Alert color="red">Не выбран админ-чат</Alert>
      </div>
    {:else}
      <GroupChat {botName} chatId={config.feedback_handler_config.admin_chat_id} />
    {/if}
    <!-- <span>x:{Math.round(position.x)},y:{Math.round(position.y)}</span> -->
  </NodeContent>
</Node>
