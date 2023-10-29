<script lang="ts">
  import { Collapse, Stack, Switch, Text } from "@svelteuidev/core";
  import type { FormResultsExport } from "../../../../api/types";
  import { PLACEHOLDER_GROUP_CHAT_ID } from "../../defaultConfigs";
  import GroupChatIdSelect from "../../../components/GroupChatIdSelect.svelte";

  export let config: FormResultsExport;
  export let botName: string;
</script>

<Stack spacing="lg">
  <Switch label="Анонимизировать ответы" bind:checked={config.is_anonymous} />
  <Text>Прислать</Text>
  <Switch label="юзер:ке" bind:checked={config.echo_to_user} />
  <Stack spacing="sm">
    <Switch
      label="в админ-чат"
      checked={config.to_chat !== null}
      on:change={(
        // @ts-expect-error
        e,
      ) => {
        if (e.target.checked) {
          config.to_chat = { chat_id: PLACEHOLDER_GROUP_CHAT_ID, via_feedback_handler: true };
        } else {
          config.to_chat = null;
        }
      }}
    />
    {#if config.to_chat}
      <div class="export-to-chat-setting-container">
        <Stack spacing="xs">
          <GroupChatIdSelect label="" {botName} bind:selectedGroupChatId={config.to_chat.chat_id} />
          <Switch
            size="xs"
            label="С возможностью ответить через бота"
            bind:checked={config.to_chat.via_feedback_handler}
          />
        </Stack>
      </div>
    {/if}
  </Stack>
</Stack>

<style>
  div.export-to-chat-setting-container {
    padding-left: 0.5em;
    border-left: 1px rgb(222, 226, 230) solid;
  }
</style>
