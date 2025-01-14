<script lang="ts">
  import { t } from "svelte-i18n";
  import { Avatar, Listgroup, ListgroupItem, Popover, Spinner } from "flowbite-svelte";
  import { ArrowUpRightFromSquareOutline, DotsHorizontalOutline, RefreshOutline } from "flowbite-svelte-icons";
  import { getBotUser } from "../api/botUser";
  import type { TgBotUser } from "../api/types";
  import { ok, type Result } from "../utils";
  import ActionIcon from "./ActionIcon.svelte";
  import ErrorBadge from "./AlertBadge.svelte";
  import DataBadge from "./internal/DataBadge.svelte";
  import DataBadgeLoader from "./internal/DataBadgeLoader.svelte";

  export let botId: string;
  export let tgBotUser: TgBotUser | null = null;
  export let inline: boolean = false;

  let botUserPromise: Promise<Result<TgBotUser>>;
  const LOCALSTORAGE_KEY = `botUserData/${botId}`;

  function saveToLocalstorage(botUser: TgBotUser) {
    localStorage.setItem(LOCALSTORAGE_KEY, JSON.stringify(botUser));
  }

  function makeUserDataAvailable(botUser: TgBotUser) {
    botUserPromise = new Promise((resolve, _) => resolve(ok(botUser)));
  }

  async function loadAndCache(): Promise<Result<TgBotUser>> {
    const res = await getBotUser(botId);
    if (res.ok) {
      saveToLocalstorage(res.data);
    }
    return res;
  }

  $: {
    if (tgBotUser !== null) {
      saveToLocalstorage(tgBotUser);
      makeUserDataAvailable(tgBotUser);
    } else {
      const stored = localStorage.getItem(LOCALSTORAGE_KEY);
      if (stored !== null) {
        makeUserDataAvailable(JSON.parse(stored));
      } else {
        botUserPromise = loadAndCache();
      }
    }
  }

  const actionsIconId = `tguser-action-icon-${botId}`;
</script>

{#if inline}
  {#await botUserPromise}
    <Spinner size={3} />
  {:then res}
    {#if res.ok}
      <slot user={res.data} />
    {:else}
      <ErrorBadge title={$t("components.bot_user_badge.data_loading_error")} text={res.error} />
    {/if}
  {/await}
{:else}
  <DataBadge>
    {#await botUserPromise}
      <DataBadgeLoader />
    {:then res}
      {#if res.ok}
        <div class="flex flex-row gap-2 items-start justify-between">
          <div class="flex flex-row gap-2 items-center">
            <Avatar src={res.data.userpic ? `data:image/png;base64,${res.data.userpic}` : undefined} class="w-6 h-6" />
            <span>
              {res.data.name}
              <br />
              <span class="text-gray-500 break-all">
                @{res.data.username}
              </span>
            </span>
          </div>
          <ActionIcon id={actionsIconId} icon={DotsHorizontalOutline} />
          <Popover triggeredBy={"#" + actionsIconId} placement="right-start" defaultClass="" class="z-10">
            <Listgroup active class="text-sm border-none">
              <ListgroupItem
                on:click={() => {
                  botUserPromise = loadAndCache();
                }}
                class="gap-2"
              >
                <RefreshOutline class="w-3 h-3 text-gray-700" />
                {$t("generic.refresh")}
              </ListgroupItem>
              <ListgroupItem
                href={`https://t.me/${res.data.username}`}
                class="gap-2 flex items-center"
                attrs={{ target: "_blank" }}
              >
                <ArrowUpRightFromSquareOutline class="w-3 h-3 text-gray-700" />
                {$t("components.bot_user_badge.go_to_bot")}
              </ListgroupItem>
            </Listgroup>
          </Popover>
        </div>
      {:else}
        <ErrorBadge title={$t("components.bot_user_badge.data_loading_error")} text={res.error} />
      {/if}
    {/await}
  </DataBadge>
{/if}
