<!--
    Group chat available to the bot, rendered with it's Telegram name, handle and avatar.
    Caches stuff in localStorage for fewer backend calls.
-->
<script lang="ts">
  import { Avatar, Listgroup, ListgroupItem, Popover } from "flowbite-svelte";
  import { DotsHorizontalOutline, RefreshOutline } from "flowbite-svelte-icons";
  import { getGroupChatData } from "../api/groupChats";
  import type { TgGroupChat } from "../api/types";
  import ErrorBadge from "../components/ErrorBadge.svelte";
  import { ok, type Result } from "../utils";
  import ActionIcon from "./ActionIcon.svelte";
  import DataBadge from "./internal/DataBadge.svelte";
  import DataBadgeLoader from "./internal/DataBadgeLoader.svelte";

  export let botId: string;
  export let chatId: number | string;
  export let chatData: TgGroupChat | null = null; // null = get from localstorage or load, if not there

  let renderedChatDataPromise: Promise<Result<TgGroupChat>>;
  const LOCALSTORAGE_KEY = `chatData/${chatId}`;

  function saveToLocalstorage(chatData: TgGroupChat) {
    localStorage.setItem(LOCALSTORAGE_KEY, JSON.stringify(chatData));
  }

  function makeChatDataAvailable(chatData: TgGroupChat) {
    renderedChatDataPromise = new Promise((resolve, _) => resolve(ok(chatData)));
  }

  async function loadAndCacheChatData() {
    const res = await getGroupChatData(botId, chatId);
    if (res.ok) {
      saveToLocalstorage(res.data);
    }
    return res;
  }

  $: {
    // NOTE: this reactive block is needed because we're fetching/loading from localStorage stuff based on chatId,
    // not rendering it directly

    if (chatData !== null) {
      saveToLocalstorage(chatData);
      makeChatDataAvailable(chatData);
    } else {
      const stored = localStorage.getItem(LOCALSTORAGE_KEY);
      if (stored !== null) {
        makeChatDataAvailable(JSON.parse(stored));
      } else {
        renderedChatDataPromise = loadAndCacheChatData();
      }
    }
  }

  const actionsIconId = `group-chat-badge-actions-icon-${chatId}`;
</script>

<DataBadge>
  <div class="flex flex-row gap-2">
    {#await renderedChatDataPromise}
      <DataBadgeLoader />
    {:then chatRes}
      {#if chatRes.ok}
        <div class="w-full flex flex-row gap-2 items-start justify-between">
          <div class="flex flex-row gap-2 items-center">
            <Avatar
              src={chatRes.data.photo ? `data:image/png;base64,${chatRes.data.photo}` : undefined}
              class="w-6 h-6"
            />
            <div>
              <span>{chatRes.data.title}</span>
              {#if chatRes.data.username}
                <span class="text-gray-500">
                  @{chatRes.data.username}
                </span>
              {/if}
            </div>
          </div>
          <ActionIcon id={actionsIconId} icon={DotsHorizontalOutline} />
          <Popover triggeredBy={"#" + actionsIconId} placement="right-start" defaultClass="">
            <Listgroup active class="text-sm border-none">
              <ListgroupItem
                on:click={() => {
                  renderedChatDataPromise = loadAndCacheChatData();
                }}
                class="gap-2"
              >
                <RefreshOutline class="w-3 h-3 text-gray-700" />
                Обновить
              </ListgroupItem>
            </Listgroup>
          </Popover>
        </div>
      {:else}
        <ErrorBadge title="Ошибка загрузки данных чата" text={chatRes.error} />
      {/if}
    {/await}
  </div>
</DataBadge>
