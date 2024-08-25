<script lang="ts">
  import { Accordion, AccordionItem, Button, Li, List, Spinner } from "flowbite-svelte";
  import { CloseOutline, PenOutline } from "flowbite-svelte-icons";
  import { onDestroy } from "svelte";
  import { getAvailableGroupChats, startGroupChatDiscovery, stopGroupChatDiscovery } from "../../api/groupChats";
  import type { TgGroupChat } from "../../api/types";
  import ButtonLoadingSpinner from "../../components/ButtonLoadingSpinner.svelte";
  import ErrorBadge from "../../components/ErrorBadge.svelte";
  import GroupChatBadge from "../../components/GroupChatBadge.svelte";
  import { ok, type Result } from "../../utils";
  import { PLACEHOLDER_GROUP_CHAT_ID } from "../nodes/defaultConfigs";

  export let label: string;
  export let botId: string;
  export let selectedGroupChatId: number | string;

  let showGroupChatSelect = selectedGroupChatId === PLACEHOLDER_GROUP_CHAT_ID;

  let availableGroupChatsPromise: Promise<Result<TgGroupChat[]>> = new Promise((resolve, _) => resolve(ok([])));

  $: {
    if (showGroupChatSelect) {
      availableGroupChatsPromise = getAvailableGroupChats(botId);
    } else {
      // on any close of the accordion we make sure to stop the discovery
      stopAdminChatDiscovery();
    }
  }

  async function stopAdminChatDiscovery() {
    if (!isDiscoveringAdminChats) {
      return;
    }
    discoverChatsPollingIntervalId !== null ? clearInterval(discoverChatsPollingIntervalId) : null;
    stopChatDiscoveryAfterTimeoutId !== null ? clearTimeout(stopChatDiscoveryAfterTimeoutId) : null;
    await stopGroupChatDiscovery(botId);
    isDiscoveringAdminChats = false;
  }

  let isDiscoveringAdminChats = false;
  let discoverChatsPollingIntervalId: number | null = null;
  let stopChatDiscoveryAfterTimeoutId: number | null = null;
  onDestroy(stopAdminChatDiscovery);
</script>

<Accordion flush>
  <AccordionItem bind:open={showGroupChatSelect} paddingFlush="py-3">
    <div slot="header" class="flex flex-col gap-2 text-gray-900">
      <span class="font-bold">{label}</span>
      {#if selectedGroupChatId !== PLACEHOLDER_GROUP_CHAT_ID}
        <GroupChatBadge {botId} chatId={selectedGroupChatId} />
      {/if}
    </div>
    <div slot="arrowdown">
      <PenOutline size="sm" />
    </div>
    <div slot="arrowup">
      <CloseOutline size="sm" />
    </div>

    <!-- accordion body -->
    <div class="flex flex-col gap-2 my-1">
      {#await availableGroupChatsPromise}
        <Spinner />
      {:then availableGroupChatsPromiseResult}
        {#if availableGroupChatsPromiseResult.ok}
          <span>Доступные чаты</span>
          {#each availableGroupChatsPromiseResult.data as availableGroupChat}
            <div class="flex items-center gap-1">
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
                <GroupChatBadge {botId} chatId={availableGroupChat.id} chatData={availableGroupChat} />
              </label>
            </div>
          {/each}
        {:else}
          <ErrorBadge title="Не получилось загрузить доступные чаты" text={availableGroupChatsPromiseResult.error} />
        {/if}
      {/await}
      <div class="flex flex-col gap-2">
        <div class="flex flew-row gap-2">
          <Button
            size="xs"
            on:click={async () => {
              isDiscoveringAdminChats = true;
              await startGroupChatDiscovery(botId);

              // update available group list each 5 seconds
              // @ts-expect-error
              discoverChatsPollingIntervalId = setInterval(() => {
                if (isDiscoveringAdminChats) {
                  console.log("Updating available group chats list");
                  availableGroupChatsPromise = getAvailableGroupChats(botId);
                } else if (discoverChatsPollingIntervalId !== null) {
                  clearInterval(discoverChatsPollingIntervalId);
                }
              }, 5 * 1000);

              // auto-stop discovery after 10 minutes
              // @ts-expect-error
              stopChatDiscoveryAfterTimeoutId = setTimeout(stopAdminChatDiscovery, 10 * 60 * 1000);
            }}
          >
            <ButtonLoadingSpinner loading={isDiscoveringAdminChats} />
            Сканировать
          </Button>
          {#if isDiscoveringAdminChats}
            <Button outline size="xs" on:click={stopAdminChatDiscovery}>Остановить</Button>
          {/if}
        </div>
        {#if isDiscoveringAdminChats}
          <!-- TODO: better instructions -->
          <List>
            <Li>В режиме сканирования добавьте бота в ваш чат, и он автоматически добавит его в список.</Li>
            <Li>
              Если бот уже в чате, используйте команду <code>/discover_chat</code>.
            </Li>
          </List>
        {/if}
      </div>
    </div>
  </AccordionItem>
</Accordion>
