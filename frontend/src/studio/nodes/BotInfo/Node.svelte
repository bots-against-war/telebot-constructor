<script lang="ts">
  import { Avatar } from "flowbite-svelte";
  import { ArrowUpRightFromSquareOutline } from "flowbite-svelte-icons";
  import { Node } from "svelvet";
  import { getBotUser } from "../../../api/botUser";
  import type { TgBotUser } from "../../../api/types";
  import ActionIcon from "../../../components/ActionIcon.svelte";
  import ErrorBadge from "../../../components/ErrorBadge.svelte";
  import DataBadge from "../../../components/internal/DataBadge.svelte";
  import DataBadgeLoader from "../../../components/internal/DataBadgeLoader.svelte";
  import { DEFAULT_START_COMMAND_ENTRYPOINT_ID } from "../../../constants";
  import type { SvelvetPosition } from "../../../types";
  import { getModalOpener, ok } from "../../../utils";
  import NodeContent from "../../components/NodeContent.svelte";
  import OutputAnchor from "../../components/OutputAnchor.svelte";
  import OutputAnchorsBox from "../../components/OutputAnchorsBox.svelte";
  import { NodeTypeKey } from "../display";
  import { DEFAULT_NODE_PROPS } from "../nodeProps";
  import Modal from "./Modal.svelte";
  import BotUserBadge from "../../../components/BotUserBadge.svelte";

  const openModal = getModalOpener<Modal>();

  export let botName: string;
  export let position: SvelvetPosition;

  let loadedBotUser: TgBotUser | null = null;

  async function loadBotUser() {
    const res = await getBotUser(botName);
    if (!res.ok) return res;
    loadedBotUser = res.data;
    return res;
  }

  let botUserPromise = loadBotUser();
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
      if (!loadedBotUser) return;
      openModal(Modal, {
        botName,
        botUser: loadedBotUser,
        onBotUserUpdated: (newBotUser) => {
          loadedBotUser = newBotUser;
          botUserPromise = new Promise((resolve, _) => resolve(ok(newBotUser)));
        },
      });
    }}
  >
    <DataBadge>
      {#await botUserPromise}
        <DataBadgeLoader />
      {:then botUserResult}
        {#if botUserResult.ok}
          <BotUserBadge botUser={botUserResult.data} />
        {:else}
          <ErrorBadge title="Ошибка загрузки данных о боте" text={botUserResult.error} />
        {/if}
      {/await}
    </DataBadge>
  </NodeContent>
  <OutputAnchorsBox>
    <OutputAnchor nextBlockId={DEFAULT_START_COMMAND_ENTRYPOINT_ID} dummy />
  </OutputAnchorsBox>
</Node>
