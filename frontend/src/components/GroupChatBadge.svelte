<!--
    Group chat available to the bot, rendered with it's Telegram name, handle and avatar.
    Caches stuff in localStorage for fewer backend calls.
-->
<script lang="ts">
  import { Alert, Group, Loader } from "@svelteuidev/core";

  import { getGroupChatData } from "../api/groupChats";
  import type { TgGroupChat } from "../api/types";
  import { ok, type Result } from "../utils";
  import { ExclamationTriangle } from "radix-icons-svelte";

  export let botName: string;
  export let chatId: number | string;
  export let chatData: TgGroupChat | null = null; // null = get from localstorage or load, if not there

  let renderedChatDataPromise: Promise<Result<TgGroupChat>>;

  $: {
    // NOTE: this reactive block is needed because we're fetching/loading from localStorage stuff based on chatId
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

<div class="container">
  {#await renderedChatDataPromise}
    <Loader size={10} />
  {:then loadChatResult}
    {#if loadChatResult.ok}
      <!-- TODO: render icons, chat type, link to chat, etc -->
      {loadChatResult.data.title}
      ({loadChatResult.data.id})
    {:else}
      <Alert color="red" title="Ошибка загрузки данных чата" icon={ExclamationTriangle}>{loadChatResult.error}</Alert>
    {/if}
  {/await}
</div>

<style>
  div.container {
    display: block;
    /* border:; */
  }
</style>
