<script lang="ts">
  import { Accordion, AccordionItem, Heading, NumberInput, Toggle } from "flowbite-svelte";
  import type { HumanOperatorBlock } from "../../../api/types";
  import InputWrapper from "../../../components/inputs/InputWrapper.svelte";
  import TextInput from "../../../components/inputs/TextInput.svelte";
  import GroupChatIdSelect from "../../components/GroupChatIdSelect.svelte";
  import LocalizableTextInput from "../../components/LocalizableTextInput.svelte";
  import NodeModalBody from "../../components/NodeModalBody.svelte";
  import NodeModalControls from "../../components/NodeModalControls.svelte";
  import { clone } from "../../utils";
  import { NODE_TITLE } from "../display";

  export let botId: string; // required for admin chat id rendering, and context does not propagate here
  export let config: HumanOperatorBlock;
  export let onConfigUpdate: (newConfig: HumanOperatorBlock) => any;

  function updateConfig() {
    fhConfig.unanswered_hashtag = unanswered || null;
    onConfigUpdate({ ...config, feedback_handler_config: fhConfig });
  }

  let fhConfig = clone(config.feedback_handler_config);
  let unanswered = fhConfig.unanswered_hashtag || "";

  const blockSeqClass = "flex flex-col gap-4";
  const blockClass = "flex flex-col gap-2";
</script>

<NodeModalBody title={NODE_TITLE.human_operator}>
  <div class={blockSeqClass}>
    <div class={blockClass}>
      <GroupChatIdSelect label="Админ-чат" {botId} bind:selectedGroupChatId={fhConfig.admin_chat_id} />
      <Toggle bind:checked={fhConfig.anonimyze_users}>Анонимизировать юзеро:к</Toggle>
      <Toggle bind:checked={fhConfig.forum_topic_per_user}>Отдельная тема на юзер:ку</Toggle>
    </div>

    <div class={blockClass}>
      <Heading tag="h6">Сообщения для юзер:ок</Heading>
      <LocalizableTextInput
        label="Ответ на успешно принятое сообщение"
        placeholder="Спасибо, мы вам скоро ответим!"
        bind:value={fhConfig.messages_to_user.forwarded_to_admin_ok}
      />
      <LocalizableTextInput
        label="Предупреждение, что сообщений слишком много"
        description="(см. Ограничение на кол-во сообщений в минуту)"
        placeholder="Не присылайте больше N сообщений в минуту!"
        bind:value={fhConfig.messages_to_user.throttling}
      />
    </div>

    <Accordion>
      <AccordionItem paddingDefault="p-3">
        <span slot="header">Дополнительно</span>
        <div class={blockSeqClass}>
          <div class={blockClass}>
            <Heading tag="h6">Сообщения для админ:ок</Heading>
            <TextInput
              placeholder="Сообщение переслано!"
              label="Уведомление о том, что ответ админки передан юзерке"
              bind:value={fhConfig.messages_to_admin.copied_to_user_ok}
            />
            <TextInput
              placeholder="Сообщение удалено из чата бота и юзерки!"
              label="Уведомление о том, что сообщение юзерке успешно удалено по команде /undo"
              bind:value={fhConfig.messages_to_admin.deleted_message_ok}
            />
            <TextInput
              placeholder="Не получилось удалить сообщение :(!"
              label="Уведомление о том, что сообщение не удалось удалить"
              bind:value={fhConfig.messages_to_admin.can_not_delete_message}
            />
          </div>
          <div class={blockClass}>
            <Heading tag="h6">Другое</Heading>
            <InputWrapper
              label="Сколько сообщений в минуту может писать пользовательница."
              description="После превышения будет софтбан."
            >
              <NumberInput bind:value={fhConfig.max_messages_per_minute} min={1} max={60} step={1} type="number" />
            </InputWrapper>
            <Toggle bind:checked={fhConfig.hashtags_in_admin_chat}>Хештеги в админ-чате</Toggle>
            {#if fhConfig.hashtags_in_admin_chat}
              <TextInput
                placeholder="#неотвечено"
                label="Текст хештега, который навешивается на новые, неотвеченные сообщения"
                bind:value={unanswered}
              />
            {/if}
          </div>
        </div>
      </AccordionItem>
    </Accordion>
  </div>
  <NodeModalControls on:save={updateConfig} />
</NodeModalBody>
