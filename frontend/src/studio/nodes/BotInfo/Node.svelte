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
</script>

<Node id={"bot-info"} bind:position {...DEFAULT_NODE_PROPS}>
  <NodeContent
    key={NodeTypeKey.info}
    colorOverride="white"
    deletable={false}
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
          <div class="flex flex-row gap-1 items-start justify-between">
            <div class="flex flex-row gap-1 items-center">
              <Avatar
                src={botUserResult.data.userpic ? `data:image/png;base64,${botUserResult.data.userpic}` : undefined}
                class="w-6 h-6"
              />
              <span>
                {botUserResult.data.name}
                <br />
                <span class="text-gray-500 break-all">
                  @{botUserResult.data.username}
                </span>
              </span>
            </div>
            <ActionIcon href={`https://t.me/${botUserResult.data.username}`} icon={ArrowUpRightFromSquareOutline} />
          </div>
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
