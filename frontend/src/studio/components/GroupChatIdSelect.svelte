<script lang="ts">
  import { Accordion, AccordionItem, Spinner } from "flowbite-svelte";
  import { CloseOutline, ExclamationCircleOutline, PenOutline } from "flowbite-svelte-icons";
  import { onDestroy } from "svelte";
  import { getAvailableGroupChats, startGroupChatDiscovery, stopGroupChatDiscovery } from "../../api/groupChats";
  import type { TgGroupChat } from "../../api/types";
  import ErrorBadge from "../../components/AlertBadge.svelte";
  import GroupChatBadge from "../../components/GroupChatBadge.svelte";
  import { PLACEHOLDER_GROUP_CHAT_ID } from "../nodes/defaultConfigs";

  export let label: string;
  export let botId: string;
  export let selectedGroupChatId: number | string;
  export let forbidNonSupergroups: boolean = true;

  // auto-open if not selected initially
  let isOpen = selectedGroupChatId === PLACEHOLDER_GROUP_CHAT_ID;

  let chatsLoadError: string | null = null;
  let availableChats: TgGroupChat[] = [];
  async function loadAvailableGroupChats() {
    const res = await getAvailableGroupChats(botId);
    if (res.ok) {
      chatsLoadError = null;
      availableChats = res.data;
    } else {
      chatsLoadError = res.error;
      availableChats = [];
      console.error("Error retrieving available group chats: ", res.error);
    }
  }

  let availableGroupChatsLoadedPromise: Promise<void> = new Promise((resolve, _) => resolve());

  $: {
    if (isOpen) {
      availableGroupChatsLoadedPromise = loadAvailableGroupChats();
      startScanning();
    } else {
      // on any close of the accordion we make sure to stop the discovery
      stopScanning();
    }
  }
  let isScannning = false;
  let discoverChatsPollingIntervalId: number | null = null;
  let stopChatDiscoveryAfterTimeoutId: number | null = null;
  async function stopScanning() {
    if (!isScannning) return;
    discoverChatsPollingIntervalId !== null ? clearInterval(discoverChatsPollingIntervalId) : null;
    stopChatDiscoveryAfterTimeoutId !== null ? clearTimeout(stopChatDiscoveryAfterTimeoutId) : null;
    await stopGroupChatDiscovery(botId);
    isScannning = false;
  }
  async function startScanning() {
    if (isScannning) return;
    isScannning = true;
    await startGroupChatDiscovery(botId);

    // update available group list each 5 seconds
    // @ts-expect-error
    discoverChatsPollingIntervalId = setInterval(async () => {
      if (isScannning) {
        console.debug("Updating available group chats list");
        await loadAvailableGroupChats();
      } else if (discoverChatsPollingIntervalId !== null) {
        clearInterval(discoverChatsPollingIntervalId);
      }
    }, 5 * 1000);
    // auto-stop discovery after 10 minutes
    // @ts-expect-error
    stopChatDiscoveryAfterTimeoutId = setTimeout(stopScanning, 10 * 60 * 1000);
  }
  onDestroy(stopScanning);

  const chatLabel = (chat: TgGroupChat) => `group-chat-${chat.id}`;
</script>

<Accordion flush>
  <AccordionItem
    bind:open={isOpen}
    paddingFlush="py-2"
    class="flex items-center justify-between w-full font-medium text-left border-gray-200"
  >
    <div slot="header" class="flex flex-row gap-3 text-gray-900 items-center">
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
    <div class="my-1 text-sm font-medium text-gray-900">
      <slot name="description" />
      {#await availableGroupChatsLoadedPromise}
        <Spinner />
      {:then}
        {#if chatsLoadError !== null}
          <ErrorBadge title="Не получилось загрузить доступные чаты" text={chatsLoadError} />
        {:else}
          <div>
            <div class="mb-2 font-bold">Доступные чаты</div>
            <div class="flex flex-col gap-2">
              {#each availableChats as chat (chat.id)}
                <div class="flex flex-row items-center gap-2">
                  <input
                    type="radio"
                    id={chatLabel(chat)}
                    bind:group={selectedGroupChatId}
                    on:change={async () => {
                      isOpen = false;
                    }}
                    value={chat.id}
                    disabled={forbidNonSupergroups && chat.type === "group"}
                  />
                  {#if forbidNonSupergroups && chat.type === "group"}
                    <ExclamationCircleOutline
                      color="red"
                      title={{
                        id: "non-supergroup chat is forbidden",
                        title: "Чат не подходит для использования в боте, его нужно активировать",
                      }}
                    />
                  {/if}
                  <label
                    for={chatLabel(chat)}
                    class={forbidNonSupergroups && chat.type === "group" ? "opacity-50" : ""}
                  >
                    <GroupChatBadge {botId} chatId={chat.id} chatData={chat} />
                  </label>
                </div>
              {/each}
            </div>
            {#if isScannning}
              <p class="mt-3">
                <Spinner size={4} class="mr-2" />
                Поиск...
              </p>
            {/if}
          </div>
        {/if}
      {/await}
    </div>
  </AccordionItem>
</Accordion>
