<!--
    Group chat available to the bot, rendered with it's Telegram name, handle and avatar.
    Caches stuff in localStorage for fewer backend calls.
-->
<script lang="ts">
  import { Alert, Loader, Image, Group, Text, Space } from "@svelteuidev/core";

  import { getGroupChatData } from "../api/groupChats";
  import type { TgGroupChat } from "../api/types";
  import { ok, type Result } from "../utils";
  import { ExclamationTriangle, QuestionMark } from "radix-icons-svelte";

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

  const OVERFLOWING_TEXT_STYLE = {
    textWrap: "nowrap",
    textOverflow: "ellipsis",
    overflow: "hidden",
  };
</script>

<div class="badge">
  <Group override={{ gap: "6px", maxWidth: "300px" }} noWrap>
    {#await renderedChatDataPromise}
      <Loader size={10} />
    {:then loadChatResult}
      {#if loadChatResult.ok}
        <!-- TODO: render icons, chat type, link to chat, etc -->
        <Image
          src={loadChatResult.data.photo !== null ? `data:image/png;base64,${loadChatResult.data.photo}` : null}
          width={25}
          height={25}
          radius={1000}
          usePlaceholder
        >
          <svelte:fragment slot="placeholder">
            <QuestionMark />
          </svelte:fragment>
        </Image>
        <Group override={{ gap: "6px" }}>
          <Text override={{ maxWidth: "250px", ...OVERFLOWING_TEXT_STYLE }}>{loadChatResult.data.title}</Text>
          {#if loadChatResult.data.username}
            <Text color="dimmed" override={{ maxWidth: "250px", ...OVERFLOWING_TEXT_STYLE }}
              >@{loadChatResult.data.username}</Text
            >
          {/if}
        </Group>
      {:else}
        <Alert color="red" title="Ошибка загрузки данных чата" icon={ExclamationTriangle}>{loadChatResult.error}</Alert>
      {/if}
    {/await}
  </Group>
</div>

<style>
  div.badge {
    padding: 5px 5px;
    border: 1px solid rgb(222, 226, 230);
    border-radius: 15px;
  }
</style>
