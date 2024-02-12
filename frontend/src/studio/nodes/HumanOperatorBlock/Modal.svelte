<script lang="ts">
  import { Accordion, Divider, NumberInput, Space, Stack, Switch, Text, TextInput } from "@svelteuidev/core";
  import type { HumanOperatorBlock } from "../../../api/types";
  import GroupChatIdSelect from "../../components/GroupChatIdSelect.svelte";
  import LocalizableTextInput from "../../components/LocalizableTextInput.svelte";
  import NodeModalControls from "../../components/NodeModalControls.svelte";
  import { NODE_TITLE } from "../display";

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
</script>

<div>
  <h3>{NODE_TITLE.human_operator}</h3>
  <Stack align="left">
    <div>
      <GroupChatIdSelect label="Выбор админ-чата" {botName} bind:selectedGroupChatId={adminChatId} />
    </div>
    <Space h="xs" />
    <Switch
      size="md"
      label="Анонимизировать юзеро_к"
      bind:checked={anonimyze_users}
      description="Присылать ли имя, юзернейм и id юзерки, или заменять его на эмоджи."
    />
    <Text size="m">Присылать ли имя, юзернейм и id юзерки, или заменять его на эмоджи.</Text>
    <Switch size="md" label="Отдельная тема на юзер_ку" bind:checked={forum_topic_per_user} />
    <Text size="m">В админ-чате создается отдельная тема на каждую юзерку, в которой будут все сообщения от нее.</Text>
  </Stack>
  <Space h="lg" />
  <Space h="lg" />
  <Text weight={"bold"} size="ьв">Сообщения для юзерок</Text>
  <Divider size="sm" />
  <Stack align="left">
    <LocalizableTextInput
      label="Ответ на успешно принятое сообщение"
      placeholder="Спасибо, мы вам скоро ответим!"
      bind:value={forwarded_to_admin_ok}
    />
    <LocalizableTextInput
      label="Предупреждение, что сообщений слишком много"
      description="(см. Ограничение на кол-во сообщений в минуту)"
      placeholder="Не присылайте больше N сообщений в минуту!"
      bind:value={throttling}
    />
  </Stack>
  <Space h="lg" />
  <Accordion variant="contained" radius="xs">
    <Accordion.Item value="advanced-settings">
      <div slot="control" style="font-weight: bold; font-size: 17px;">Дополнительные настройки</div>
      <Text weight={"bold"} size="sm">Сообщения для админок</Text>
      <Divider size="md" />
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
      <Space h="lg" />
      <Text weight={"bold"} size="sm">Еще настройки</Text>
      <Divider size="md" />
      <Stack align="left">
        <NumberInput
          bind:value={max_messages_per_minute}
          label="Сколько сообщений в минуту может писать пользовательница."
          description="После превышения будет софтбан."
          min={1}
          max={60}
          step={1}
          type="number"
        />
        <Switch size="md" label="Хештеги в админ-чате" bind:checked={hashtags_in_admin_chat} />
        {#if hashtags_in_admin_chat}
          <TextInput
            placeholder="#неотвечено"
            label="Текст хештега, который навешивается на новые, неотвеченные сообщения"
            bind:value={unanswered_hashtag}
          />
        {/if}
      </Stack>
    </Accordion.Item>
  </Accordion>

  <NodeModalControls on:save={updateConfig} />
</div>
