<script lang="ts">
  import { Node } from "svelvet";
  import type { TgBotUser } from "../../../api/types";
  import BotUserBadge from "../../../components/BotUserBadge.svelte";
  import { DEFAULT_START_COMMAND_ENTRYPOINT_ID } from "../../../constants";
  import type { SvelvetPosition } from "../../../types";
  import { getModalOpener } from "../../../utils";
  import NodeContent from "../../components/NodeContent.svelte";
  import OutputAnchor from "../../components/OutputAnchor.svelte";
  import OutputAnchorsBox from "../../components/OutputAnchorsBox.svelte";
  import { NodeTypeKey } from "../display";
  import { DEFAULT_NODE_PROPS } from "../nodeProps";
  import Modal from "./Modal.svelte";

  const openModal = getModalOpener<Modal>();

  export let botId: string;
  export let position: SvelvetPosition;
  let tgBotUser: TgBotUser | null = null; // for optimistic update after editing
  let id = "bot-user";
</script>

<Node {id} bind:position {...DEFAULT_NODE_PROPS}>
  <NodeContent
    {id}
    key={NodeTypeKey.info}
    colorOverride="white"
    deletable={false}
    clonable={false}
    on:edit={() => {
      openModal(Modal, {
        botId,
        onBotUserUpdated: (newBotUser) => {
          tgBotUser = newBotUser;
        },
      });
    }}
  >
    <BotUserBadge {botId} {tgBotUser} />
  </NodeContent>
  <OutputAnchorsBox>
    <OutputAnchor nextBlockId={DEFAULT_START_COMMAND_ENTRYPOINT_ID} dummy />
  </OutputAnchorsBox>
</Node>
