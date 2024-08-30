<script lang="ts">
  import { A, Li, List, Select, Toggle } from "flowbite-svelte";
  import type { FormResultUserAttribution, FormResultsExport } from "../../../../api/types";
  import { formResultsPagePath } from "../../../../routeUtils";
  import GroupChatIdSelect from "../../../components/GroupChatIdSelect.svelte";
  import { PLACEHOLDER_GROUP_CHAT_ID } from "../../defaultConfigs";
  import BotUserBadge from "../../../../components/BotUserBadge.svelte";
  import InputWrapper from "../../../../components/inputs/InputWrapper.svelte";
  import BlockNameInline from "../../../components/BlockNameInline.svelte";
  import { NodeTypeKey } from "../../display";

  export let config: FormResultsExport;
  export let botId: string;
  export let blockId: string;

  const userAttributionOptions: { value: FormResultUserAttribution; name: string }[] = [
    { value: "none", name: "Не сохранять" },
    { value: "unique_id", name: "Только анонимизированный идентификатор" },
    { value: "name", name: "Только имя Telegram-аккаунта" },
    { value: "full", name: "Имя и ссылку на Telegram" },
  ];
</script>

<div class="flex flex-col gap-5">
  <div class="flex flex-col gap-3">
    <h3 class="font-bold">Личные данные</h3>
    <Select placeholder="" items={userAttributionOptions} bind:value={config.user_attribution} />
    <div class="text-sm text-gray-600">
      {#if config.user_attribution == "none"}
        Ответы будут полностью анонимны
      {:else if config.user_attribution == "unique_id"}
        Ответы будут помечены анонимизированным идентификатором из эмоджи (например, "🚒🧸🕐🧔🏙🏣"). По нему можно
        будет отличить ответы одно:й пользователь:ницы, но невозможно установить личные данные.
      {:else if config.user_attribution == "name"}
        К ответу будет добавлено текущее имя Telegram-аккаунта пользователь:ницы
      {:else if config.user_attribution == "full"}
        К ответу будут добавлены полные данные Telegram аккаунта пользователь:ницы: имя, @юзернейм, user id
      {/if}
    </div>
  </div>
  <div class="flex flex-col gap-3">
    <h3 class="font-bold">Ответы на форму</h3>
    <Toggle bind:checked={config.echo_to_user}>Отправлять пользователь:нице</Toggle>
    <Toggle bind:checked={config.to_store}
      >Сохранять в&nbsp;
      {#if config.to_store}
        <A href={formResultsPagePath(botId, blockId)} target="_blank">конструктор</A>
      {:else}
        <span>конструктор</span>
      {/if}
      &nbsp;(можно найти на странице управления ботом)
    </Toggle>
    <div class="flex flex-col gap-1">
      <Toggle
        checked={config.to_chat !== null}
        on:change={(e) => {
          // @ts-expect-error
          if (e.target.checked) {
            config.to_chat = { chat_id: PLACEHOLDER_GROUP_CHAT_ID, via_feedback_handler: false };
          } else {
            config.to_chat = null;
          }
        }}>Отправлять в чат</Toggle
      >
      {#if config.to_chat}
        <div class="p-2 m-2 border-l-2 border-grey-600 flex flex-col gap-3">
          <GroupChatIdSelect
            label="Чат"
            {botId}
            bind:selectedGroupChatId={config.to_chat.chat_id}
            forbidLegacyGroups={false}
          >
            <div slot="description">
              <p>В этот чат будут пересылаться все ответы на форму.</p>
              <details class="my-2">
                <summary>Как создать чат?</summary>
                <List tag="ol">
                  <Li>
                    Откройте Telegram и добавьте вашего бота (<BotUserBadge {botId} inline let:user
                      ><code>@{user.username}</code></BotUserBadge
                    >) в новую или существующую группу
                  </Li>
                  <Li>Вернитесь в конструктор и выберите созданный чат</Li>
                  <Li>
                    Если чат не виден в списке, вернитесь в Telegram, убедитесь, что бот добавлен в чат, и отправьте в
                    него команду
                    <BotUserBadge {botId} inline let:user><code>/discover_chat@{user.username}</code></BotUserBadge>
                  </Li>
                </List>
              </details>
            </div>
          </GroupChatIdSelect>
          <InputWrapper label="Обратная связь через бота" required={false}>
            <Toggle bind:checked={config.to_chat.via_feedback_handler}>Включить</Toggle>
            {#if config.to_chat.via_feedback_handler}
              <div class="text-sm text-gray-700">
                Чтобы эта функция работала корректно, на этот же чат должен быть настроен блок
                <BlockNameInline key={NodeTypeKey.human_operator} />!
              </div>
            {/if}
          </InputWrapper>
        </div>
      {/if}
    </div>
  </div>
</div>
