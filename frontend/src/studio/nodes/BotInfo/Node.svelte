<script lang="ts">
  import { Node } from "svelvet";
  import Modal from "./Modal.svelte";
  import NodeContent from "../../components/NodeContent.svelte";
  import OutputAnchorsBox from "../../components/OutputAnchorsBox.svelte";
  import OutputAnchor from "../../components/OutputAnchor.svelte";
  import { ActionIcon, Group, Image } from "@svelteuidev/core";
  import { ArrowUpRightFromSquareOutline, QuestionCircleOutline } from "flowbite-svelte-icons";

  import ErrorBadge from "../../../components/ErrorBadge.svelte";
  import DataBadge from "../../../components/internal/DataBadge.svelte";
  import EllipsisText from "../../../components/internal/EllipsisText.svelte";
  import DataBadgeLoader from "../../../components/internal/DataBadgeLoader.svelte";

  import { DEFAULT_NODE_PROPS } from "../nodeProps";
  import { NodeTypeKey } from "../display";
  import { getBotUser } from "../../../api/botUser";
  import { getModalOpener, ok } from "../../../utils";
  import type { SvelvetPosition } from "../../../types";
  import type { TgBotUser } from "../../../api/types";
  import { DEFAULT_START_COMMAND_ENTRYPOINT_ID } from "../../../constants";

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
          <Group noWrap position="apart" spacing="xs">
            <Group override={{ gap: "6px" }}>
              <Image
                src={botUserResult.data.userpic !== null ? `data:image/png;base64,${botUserResult.data.userpic}` : null}
                width={25}
                height={25}
                radius={1000}
                usePlaceholder
              >
                <svelte:fragment slot="placeholder">
                  <QuestionCircleOutline />
                </svelte:fragment>
              </Image>
              <EllipsisText size="sm" weight="bold" maxWidth="150px">
                {botUserResult.data.name}
              </EllipsisText>
              <EllipsisText size="sm" color="dimmed" maxWidth="90px">@{botUserResult.data.username}</EllipsisText>
            </Group>
            <ActionIcon size={15} root="a" href={`https://t.me/${botUserResult.data.username}`} external>
              <ArrowUpRightFromSquareOutline />
            </ActionIcon>
          </Group>
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
