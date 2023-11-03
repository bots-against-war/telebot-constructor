<script lang="ts">
  import type { HumanOperatorBlock } from "../../../api/types";
  import NodeModalControls from "../../components/NodeModalControls.svelte";
  import GroupChatIdSelect from "../../components/GroupChatIdSelect.svelte";
  import { NODE_TITLE } from "../display";
  import {
    ActionIcon,
    Badge,
    Button,
    Group,
    NumberInput,
    Radio,
    Stack,
    Switch, Tabs,
    TextInput,
    Tooltip
  } from "@svelteuidev/core";
  import { Rocket } from "radix-icons-svelte";

  export let botName: string; //required for admin chat id rendering, and context does not propagate here
  export let config: HumanOperatorBlock;
  export let onConfigUpdate: (newConfig: HumanOperatorBlock) => any;

  function updateConfig() {
    config.feedback_handler_config.admin_chat_id = adminChatId;
    config.feedback_handler_config.anonimyze_users = anonimyze_users;
    config.feedback_handler_config.max_messages_per_minute = max_messages_per_minute;
    config.feedback_handler_config.forum_topic_per_user = forum_topic_per_user;

    config.feedback_handler_config.messages_to_user.forwarded_to_admin_ok = forwarded_to_admin_ok;
    config.feedback_handler_config.messages_to_user.throttling = throttling;

    config.feedback_handler_config.messages_to_admin.copied_to_user_ok = copied_to_user_ok;
    config.feedback_handler_config.messages_to_admin.deleted_message_ok = deleted_message_ok;
    config.feedback_handler_config.messages_to_admin.can_not_delete_message = can_not_delete_message;

    config.feedback_handler_config.hashtags_in_admin_chat = hashtags_in_admin_chat;
    config.feedback_handler_config.unanswered_hashtag = unanswered_hashtag;
    config.feedback_handler_config.message_log_to_admin_chat = message_log_to_admin_chat;

    onConfigUpdate(config);
  }

  let adminChatId = config.feedback_handler_config.admin_chat_id;
  let anonimyze_users = config.feedback_handler_config.anonimyze_users;
  let max_messages_per_minute = config.feedback_handler_config.max_messages_per_minute;
  let forum_topic_per_user = config.feedback_handler_config.forum_topic_per_user;

  let forwarded_to_admin_ok = config.feedback_handler_config.messages_to_user.forwarded_to_admin_ok;
  let throttling = config.feedback_handler_config.messages_to_user.throttling;

  let copied_to_user_ok = config.feedback_handler_config.messages_to_admin.copied_to_user_ok;
  let deleted_message_ok = config.feedback_handler_config.messages_to_admin.deleted_message_ok;
  let can_not_delete_message = config.feedback_handler_config.messages_to_admin.can_not_delete_message;

  let hashtags_in_admin_chat = config.feedback_handler_config.hashtags_in_admin_chat;
  let unanswered_hashtag = config.feedback_handler_config.unanswered_hashtag;
  let message_log_to_admin_chat = config.feedback_handler_config.message_log_to_admin_chat;
</script>

<div>
  <h1>{NODE_TITLE.language_select}</h1>
  <Tabs orientation="vertical">
    <Tabs.Tab label="Главные настройки">
      <Stack align="left">
        <div>
          <GroupChatIdSelect label="Выбор админ-чата" {botName} bind:selectedGroupChatId={adminChatId} />
        </div>
        <Tooltip
          wrapLines
          width={220}
          withArrow
          transitionDuration={200}
          label="После превышения будет софтбан."
        >
          <NumberInput
            bind:value={max_messages_per_minute}
            label="Сколько сообщений в минуту может писать пользовательница."
            min={1}
            max={60}
            step={1}
            type="number"
          />
        </Tooltip>
        <Tooltip
          wrapLines
          width="220"
          withArrow
          transitionDuration={200}
          label="присылать ли имя, юзернейм и id юзерки, или заменять его на эмоджи."
        >
          <Switch size="md" onLabel="ON" offLabel="OFF" label="Анонимизировать юзеро_к"
                  bind:checked={anonimyze_users} />
        </Tooltip>
        <Tooltip
          wrapLines
          width="220"
          withArrow
          transitionDuration={200}
          label="режим работы, где на каждую юзерку в админ-чате создается отдельная тема (позволяет выделить переписку с каждой юзеркой из общего потока)."
        >
          <Switch size="md" onLabel="ON" offLabel="OFF" label="Отдельная тема на юзер_ку"
                  bind:checked={forum_topic_per_user} />
        </Tooltip>
      </Stack>
    </Tabs.Tab>
    <Tabs.Tab label="Сообщения для юзерок">
      <Stack align="left">
        <TextInput
          placeholder="Спасибо, мы вам скоро ответим!"
          label="Ответ на успешно принятое сообщение"
          bind:value={forwarded_to_admin_ok}
        />
        <TextInput
          placeholder="Не присылайте больше N сообщений в минуту!"
          label="Предупреждение, что сообщений слишком много (см. Ограничение на кол-во сообщений в минуту)"
          bind:value={throttling}
        />
      </Stack>
    </Tabs.Tab>
    <Tabs.Tab label="Сообщения для админок">
      <Stack align="left">
        <TextInput
          placeholder="Сообщение переслано!"
          label="Уведомление о том, что ответ админки передан юзерке"
          bind:value={copied_to_user_ok}
        />
        <TextInput
          placeholder="Сообщение удалено из чата бота и юзерки!"
          label="Уведомление о том, что сообщение юзерке успешно удалено по команде /undo"
          bind:value={deleted_message_ok}
        />
        <TextInput
          placeholder="Не получилось удалить сообщение :(!"
          label="Уведомление о том, что сообщение не удалось удалить"
          bind:value={can_not_delete_message}
        />
      </Stack>
    </Tabs.Tab>
    <Tabs.Tab label="Дополнительные настройки">
      <Stack align="left">
        <Switch size="md" onLabel="ON" offLabel="OFF" label="По команде /log присылать лог сообщений в админ чат"
                bind:checked={message_log_to_admin_chat} />
        <Switch size="md" onLabel="ON" offLabel="OFF" label="Хештеги в админ-чате"
                bind:checked={hashtags_in_admin_chat} />
        {#if hashtags_in_admin_chat}
          <TextInput
            placeholder="#неотвечено"
            label="Текст хештега, который навешивается на новые, неотвеченные сообщения"
            bind:value={unanswered_hashtag}
          />
        {/if}
      </Stack>
    </Tabs.Tab>
  </Tabs>
  <NodeModalControls on:save={updateConfig} />
</div>
