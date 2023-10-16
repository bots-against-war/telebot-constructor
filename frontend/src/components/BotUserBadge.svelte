<!-- Data badge with info about a bot and action icons to edit or replace it; loads a bot user on each render -->

<script lang="ts">
  import { Group, Image, ActionIcon } from "@svelteuidev/core";
  import { QuestionMark, OpenInNewWindow, Gear, Update } from "radix-icons-svelte";

  import { getBotUser } from "../api/botUser";
  import ErrorBadge from "./ErrorBadge.svelte";
  import DataBadge from "./internal/DataBadge.svelte";
  import EllipsisText from "./internal/EllipsisText.svelte";
  import DataBadgeLoader from "./internal/DataBadgeLoader.svelte";
  import { getModalOpener, ok } from "../utils";
  import EditBotUserModal from "./internal/EditBotUserModal.svelte";
  import ReplaceBotUserModal from "./internal/ReplaceBotUserModal.svelte";

  const openModal = getModalOpener();

  export let botName: string;

  let botUserPromise = getBotUser(botName);
</script>

<DataBadge>
  {#await botUserPromise}
    <DataBadgeLoader />
  {:then botUserResult}
    {#if botUserResult.ok}
      <Group position="apart" spacing="xs">
        <Group override={{ gap: "6px" }}>
          <Image
            src={botUserResult.data.userpic !== null ? `data:image/png;base64,${botUserResult.data.userpic}` : null}
            width={30}
            height={30}
            radius={1000}
            usePlaceholder
          >
            <svelte:fragment slot="placeholder">
              <QuestionMark />
            </svelte:fragment>
          </Image>
          <EllipsisText weight="bold" maxWidth="200px">
            {botUserResult.data.name}
          </EllipsisText>
          <EllipsisText color="dimmed" maxWidth="200px">@{botUserResult.data.username}</EllipsisText>
        </Group>
        <Group override={{ gap: "0" }}>
          <ActionIcon
            on:click={() => {
              openModal(EditBotUserModal, {
                botName: botName,
                botUser: botUserResult.data,
                // @ts-ignore
                onBotUserUpdated: (newBotUser) =>
                  (botUserPromise = new Promise((resolve, _) => resolve(ok(newBotUser)))),
              });
            }}
          >
            <Gear />
          </ActionIcon>
          <!-- <ActionIcon
            on:click={() => {
              openModal(ReplaceBotUserModal, {
                botName: botName,
                // @ts-ignore
                onNewTokenSecretName: (newTokenSecretName) => {
                  // TODO:
                  // - replace ONLY token secret name (e.g. via a dedicated endpoint), also set it in frontend code
                  // - update UI so that the new bot info is loaded
                },
              });
            }}
          >
            <Update />
          </ActionIcon> -->
          <ActionIcon root="a" href={`https://t.me/${botUserResult.data.username}`} external>
            <OpenInNewWindow />
          </ActionIcon>
        </Group>
      </Group>
    {:else}
      <ErrorBadge title="Ошибка загрузки данных о боте" text={botUserResult.error} />
    {/if}
  {/await}
</DataBadge>
