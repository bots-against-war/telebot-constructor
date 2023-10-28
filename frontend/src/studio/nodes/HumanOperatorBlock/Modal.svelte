<script lang="ts">
  import type { HumanOperatorBlock } from "../../../api/types";
  import NodeModalControls from "../../components/NodeModalControls.svelte";
  import GroupChatIdSelect from "../../components/GroupChatIdSelect.svelte";
  import {
    ActionIcon,
    Badge,
    Button,
    Group,
    NumberInput,
    Radio,
    Stack,
    Switch,
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

    onConfigUpdate(config);
  }

  let errorMessage = "";
  let adminChatId = config.feedback_handler_config.admin_chat_id;
  let anonimyze_users = config.feedback_handler_config.anonimyze_users;
  let max_messages_per_minute = config.feedback_handler_config.max_messages_per_minute;
  let forum_topic_per_user = config.feedback_handler_config.forum_topic_per_user;

  let forwarded_to_admin_ok = config.feedback_handler_config.messages_to_user.forwarded_to_admin_ok;
  let throttling = config.feedback_handler_config.messages_to_user.throttling;

  let copied_to_user_ok = config.feedback_handler_config.messages_to_admin.copied_to_user_ok;
  let deleted_message_ok = config.feedback_handler_config.messages_to_admin.deleted_message_ok;
  let can_not_delete_message = config.feedback_handler_config.messages_to_admin.can_not_delete_message;

</script>

<div>
  <h1>Человек-оператор</h1>
  <div style="margin-top: 1em;">
    <Stack override={{ height: 300 }} align="left">
      <h3>Главные настройки</h3>
      <div>
        <GroupChatIdSelect label="Выбор админ-чата" {botName} bind:selectedGroupChatId={adminChatId} />
      </div>

      <Tooltip
        wrapLines
        width="220"
        withArrow
        transitionDuration={200}
        label="присылать ли имя, юзернейм и id юзерки, или заменять его на эмоджи."
      >
        <Switch size="lg" onLabel="ON" offLabel="OFF" label="Анонимизировать юзеро_к"
                bind:checked={anonimyze_users} />
      </Tooltip>
      <Tooltip
        wrapLines
        width="220"
        withArrow
        transitionDuration={200}
        label="режим работы, где на каждую юзерку в админ-чате создается отдельная тема (позволяет выделить переписку с каждой юзеркой из общего потока)."
      >
        <Switch size="lg" onLabel="ON" offLabel="OFF" label="Отдельная тема на юзер_ку"
                bind:checked={forum_topic_per_user} />
      </Tooltip>

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
    </Stack>

    <Stack override={{ height: 300 }} align="left">
      <h3>Сообщения для юзерок</h3>

      <TextInput
        placeholder="Спасибо, мы вам скоро ответим!"
        label="ответ на успешно принятое сообщение"
        bind:forwarded_to_admin_ok
      />
      <TextInput
        placeholder="Не присылайте больше N сообщений в минуту!"
        label="предупреждение, что сообщений слишком много (см. max_messages_per_minute)"
        bind:throttling
      />
    </Stack>
    <Stack override={{ height: 300 }} align="left">
      <h3>Сообщения для админок</h3>

      <TextInput
        placeholder="Спасибо, мы вам скоро ответим!"
        label="уведомление что ответ админки передан юзерке"
        bind:copied_to_user_ok
      />
      <TextInput
        placeholder="Не присылайте больше N сообщений в минуту!"
        label="предупреждение, что сообщений слишком много (см. max_messages_per_minute)"
        bind:throttling
      />

    </Stack>

  <NodeModalControls on:save={updateConfig} />
  </div>
</div>
