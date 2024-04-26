<script lang="ts">
  import { Heading, Toggle } from "flowbite-svelte";
  import type { FormResultsExport } from "../../../../api/types";
  import GroupChatIdSelect from "../../../components/GroupChatIdSelect.svelte";
  import { PLACEHOLDER_GROUP_CHAT_ID } from "../../defaultConfigs";

  export let config: FormResultsExport;
  export let botName: string;
</script>

<div class="flex flex-col gap-5">
  <div class="flex flex-col gap-3">
    <h3 class="font-bold">Анонимизация</h3>
    <Toggle bind:checked={config.is_anonymous}>
      {#if config.is_anonymous}
        Личные данные
      {/if}
    </Toggle>
  </div>
  <div class="flex flex-col gap-3">
    <h3 class="font-bold">Отправлять ответы</h3>
    <Toggle bind:checked={config.echo_to_user}>юзер:ке</Toggle>
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
        }}>в чат</Toggle
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
