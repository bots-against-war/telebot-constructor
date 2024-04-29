<script lang="ts">
  import { A, Select, Toggle } from "flowbite-svelte";
  import type { FormResultUserAttribution, FormResultsExport } from "../../../../api/types";
  import { formResultsPagePath } from "../../../../routeUtils";
  import GroupChatIdSelect from "../../../components/GroupChatIdSelect.svelte";
  import { PLACEHOLDER_GROUP_CHAT_ID } from "../../defaultConfigs";

  export let config: FormResultsExport;
  export let botName: string;
  export let blockId: string;

  const userAttributionOptions: { value: FormResultUserAttribution; name: string }[] = [
    { value: "none", name: "Не сохранять" },
    { value: "unique_id", name: "Только анонимизированный идентификатор" },
    { value: "name", name: "Только имя телеграм-аккаунта" },
    { value: "full", name: "Имя и ссылку на телеграм" },
  ];
</script>

<div class="flex flex-col gap-5">
  <div class="flex flex-col gap-3">
    <h3 class="font-bold">Личные данные юзер:ки</h3>
    <Select placeholder="" items={userAttributionOptions} bind:value={config.user_attribution} />
    <div class="text-sm text-gray-600">
      {#if config.user_attribution == "none"}
        Ответы будут полностью анонимны, без возможности установить автор:ку
      {:else if config.user_attribution == "unique_id"}
        Ответы будут помечены анонимизированным идентификатором из эмоджи (например, "🚒🧸🕐🧔🏙🏣"). По нему можно
        будет отличить ответы одно:й юзер:ки, но невозможно отследить е:ё личные данные.
      {:else if config.user_attribution == "name"}
        К ответу будет добавлено текущее имя телеграм-аккаунта юзер:ки
      {:else if config.user_attribution == "full"}
        К ответу будут добавлены полные данные телеграм аккаунта юзер:ки: имя, @юзернейм, user id
      {/if}
    </div>
  </div>
  <div class="flex flex-col gap-3">
    <h3 class="font-bold">Ответы на форму</h3>
    <Toggle bind:checked={config.to_store}
      >Сохранять в&nbsp;
      {#if config.to_store}
        <A href={formResultsPagePath(botName, blockId)} target="_blank">память бота</A>
      {:else}
        <span>память бота</span>
      {/if}
    </Toggle>
    <Toggle bind:checked={config.echo_to_user}>Отправлять юзер:ке</Toggle>
    <div class="flex flex-col gap-1">
      <Toggle
        checked={config.to_chat !== null}
        on:change={(e) => {
          // @ts-expect-error
          if (e.target.checked) {
            config.to_chat = { chat_id: PLACEHOLDER_GROUP_CHAT_ID, via_feedback_handler: true };
          } else {
            config.to_chat = null;
          }
        }}>Отправлять в чат</Toggle
      >
      {#if config.to_chat}
        <div class="p-2 m-2 border-l-2 border-grey-600 flex flex-col gap-3">
          <GroupChatIdSelect label="" {botName} bind:selectedGroupChatId={config.to_chat.chat_id} />
          <Toggle bind:checked={config.to_chat.via_feedback_handler}>С возможностью ответить через бота</Toggle>
        </div>
      {/if}
    </div>
  </div>
</div>
