<!--
    Group chat available to the bot, rendered with it's Telegram name, handle and avatar.
    Caches stuff in localStorage for fewer backend calls.
-->
<script lang="ts">
  import { Avatar } from "flowbite-svelte";
  import { getGroupChatData } from "../api/groupChats";
  import type { TgGroupChat } from "../api/types";
  import ErrorBadge from "../components/ErrorBadge.svelte";
  import { ok, type Result } from "../utils";
  import DataBadge from "./internal/DataBadge.svelte";
  import DataBadgeLoader from "./internal/DataBadgeLoader.svelte";

  export let botName: string;
  export let chatId: number | string;
  export let chatData: TgGroupChat | null = null; // null = get from localstorage or load, if not there

  let renderedChatDataPromise: Promise<Result<TgGroupChat>>;

  $: {
    // NOTE: this reactive block is needed because we're fetching/loading from localStorage stuff based on chatId,
    // not rendering it directly

    const LOCALSTORAGE_PREFIX = "chat-data-for";
    let localStoragePrefix = `${LOCALSTORAGE_PREFIX}${chatId}`;

    function saveToCache(chatData: TgGroupChat) {
      localStorage.setItem(localStoragePrefix, JSON.stringify(chatData));
    }

    function chatDataAvailable(chatData: TgGroupChat) {
      renderedChatDataPromise = new Promise((resolve, _) => resolve(ok(chatData)));
    }

    async function loadAndSaveChatData() {
      const res = await getGroupChatData(botName, chatId);
      if (res.ok) {
        saveToCache(res.data);
      }
      return res;
    }

    if (chatData !== null) {
      saveToCache(chatData);
      chatDataAvailable(chatData);
    } else {
      let storedChatJson = localStorage.getItem(localStoragePrefix);
      if (storedChatJson !== null) {
        chatDataAvailable(JSON.parse(storedChatJson));
      } else {
        renderedChatDataPromise = loadAndSaveChatData();
      }
    }
  }
</script>

<DataBadge>
  <div class="flex flex-row gap-2 mr-1 max-w-60">
    {#await renderedChatDataPromise}
      <DataBadgeLoader />
    {:then loadChatResult}
      {#if loadChatResult.ok}
        <!-- TODO: render icons, chat type, link to chat, etc -->
        <Avatar
          src={loadChatResult.data.photo ? `data:image/png;base64,${loadChatResult.data.photo}` : undefined}
          class="w-6 h-6"
        />
        <div>
          <span>{loadChatResult.data.title}</span>
          {#if loadChatResult.data.username}
            <span class=" text-gray-500">
              @{loadChatResult.data.username}
            </span>
          {/if}
        </div>
      {:else}
        <ErrorBadge title="Ошибка загрузки данных чата" text={loadChatResult.error} />
      {/if}
    {/await}
  </div>
</DataBadge>
