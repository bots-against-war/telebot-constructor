<script lang="ts">
  import { onDestroy } from "svelte";
  import {
    InputWrapper,
    Collapse,
    Group,
    ActionIcon,
    Stack,
    Space,
    Loader,
    Button,
    Text,
    Paper,
  } from "@svelteuidev/core";
  import { Cross1, Pencil1 } from "radix-icons-svelte";

  import GroupChatBadge from "../../components/GroupChatBadge.svelte";

  import { PLACEHOLDER_GROUP_CHAT_ID } from "../nodes/defaultConfigs";
  import type { TgGroupChat } from "../../api/types";
  import { ok, type Result } from "../../utils";
  import { getAvailableGroupChats, startGroupChatDiscovery, stopGroupChatDiscovery } from "../../api/groupChats";
  import ErrorBadge from "../../components/ErrorBadge.svelte";

  export let label: string;
  export let botName: string;
  export let selectedGroupChatId: number | string;

  let showGroupChatSelect = selectedGroupChatId === PLACEHOLDER_GROUP_CHAT_ID;

  let availableGroupChatsPromise: Promise<Result<TgGroupChat[]>> = new Promise((resolve, _) => resolve(ok([])));

  $: if (showGroupChatSelect) {
    availableGroupChatsPromise = getAvailableGroupChats(botName);
  }

  async function stopAdminChatDiscovery() {
    isDiscoveringAdminChats = false;
    discoverChatsPollingIntervalId !== null ? clearInterval(discoverChatsPollingIntervalId) : null;
    stopChatDiscoveryAfterTimeoutId !== null ? clearTimeout(stopChatDiscoveryAfterTimeoutId) : null;
    await stopGroupChatDiscovery(botName);
  }

  let isDiscoveringAdminChats = false;
  let discoverChatsPollingIntervalId: number | null = null;
  let stopChatDiscoveryAfterTimeoutId: number | null = null;
  onDestroy(stopAdminChatDiscovery);
</script>

<InputWrapper {label}>
  {#if selectedGroupChatId !== PLACEHOLDER_GROUP_CHAT_ID}
    <Group>
      <GroupChatBadge {botName} chatId={selectedGroupChatId} />
      <ActionIcon
        on:click={async () => {
          showGroupChatSelect = !showGroupChatSelect;
          await stopAdminChatDiscovery();
        }}
      >
        {#if showGroupChatSelect}
          <Cross1 />
        {:else}
          <Pencil1 />
        {/if}
      </ActionIcon>
    </Group>
  {/if}
  <Collapse open={showGroupChatSelect}>
    <Space h="sm" />
    <Paper withBorder>
      <Stack spacing="xs">
        {#await availableGroupChatsPromise}
          <Loader size="xs" />
        {:then availableGroupChatsPromiseResult}
          {#if availableGroupChatsPromiseResult.ok}
            <Stack spacing="xs" override={{ gap: "5px" }}>
              <Text color="dimmed">Доступные чаты</Text>
              {#each availableGroupChatsPromiseResult.data as availableGroupChat}
                <div class="radio-button">
                  <input
                    type="radio"
                    id={`group-chat-${availableGroupChat.id}`}
                    bind:group={selectedGroupChatId}
                    on:change={async () => {
                      showGroupChatSelect = false;
                      await stopAdminChatDiscovery();
                    }}
                    value={availableGroupChat.id}
                  />
                  <label for={`group-chat-${availableGroupChat.id}`}>
                    <GroupChatBadge {botName} chatId={availableGroupChat.id} chatData={availableGroupChat} />
                  </label>
                </div>
              {/each}
            </Stack>
          {:else}
            <ErrorBadge title="Не получилось загрузить доступные чаты" text={availableGroupChatsPromiseResult.error} />
          {/if}
        {/await}
        <Stack spacing="xs">
          <Group>
            <Button
              size="xs"
              compact
              loading={isDiscoveringAdminChats}
              on:click={async () => {
                isDiscoveringAdminChats = true;
                await startGroupChatDiscovery(botName);

                // update available group list each 5 seconds
                // @ts-expect-error
                discoverChatsPollingIntervalId = setInterval(() => {
                  if (isDiscoveringAdminChats) {
                    console.log("Updating available group chats list");
                    availableGroupChatsPromise = getAvailableGroupChats(botName);
                  } else if (discoverChatsPollingIntervalId !== null) {
                    clearInterval(discoverChatsPollingIntervalId);
                  }
                }, 5 * 1000);

                // auto-stop discovery after 10 minutes
                // @ts-expect-error
                stopChatDiscoveryAfterTimeoutId = setTimeout(stopAdminChatDiscovery, 10 * 60 * 1000);
              }}
            >
              Сканировать
            </Button>
            {#if isDiscoveringAdminChats}
              <Button size="xs" compact variant="outline" on:click={stopAdminChatDiscovery}>Остановить</Button>
            {/if}
          </Group>
          {#if isDiscoveringAdminChats}
            <Text>
              <ul>
                <li>В режиме сканирования добавьте бота в ваш чат, и он автоматически добавит его в список.</li>
                <li>
                  Если бот уже в чате, используйте команду <code>/discover_chat</code>.
                </li>
              </ul>
            </Text>
          {/if}
        </Stack>
      </Stack>
    </Paper>
  </Collapse>
  <!-- <NumberInput hideControls placeholder={label} {label} bind:value={selectedGroupChatId} /> -->
</InputWrapper>

<style>
  div.radio-button {
    display: flex;
    align-items: center;
    gap: 0.2em;
  }
  ul {
    margin: 0;
    padding-left: 1.2em;
  }
</style>
