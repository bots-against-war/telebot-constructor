<script lang="ts">
  import { saveBotConfig } from "../api/botConfig";
  import { Button, Flex, PasswordInput, TextInput } from "@svelteuidev/core";
  import { createBotTokenSecret, getError, getModalCloser, unwrap } from "../utils";
  import { slugify } from "transliteration";
  import { validateBotToken } from "../api/validation";
  import type { BotConfig, BotInfo } from "../api/types";
  import ErrorBadge from "../components/ErrorBadge.svelte";
  import { getBotInfo } from "../api/botInfo";
  import { BOT_INFO_NODE_ID, DEFAULT_START_COMMAND_ENTRYPOINT_ID } from "../constants";

  export let newBotCallback: (botName: string, info: BotInfo) => void;

  const closePopup = getModalCloser();

  let botDisplayNameInput = "";
  let botTokenInput = "";
  let errorTitle: string | null = null;
  let error: string | null = null;
  let isCreating = false;
  let userClickedCreate = false;

  async function createNewBot() {
    userClickedCreate = true;
    let botToken = botTokenInput.trim();
    let botDisplayName = botDisplayNameInput.trim();
    if (!botDisplayName) {
      errorTitle = "Не хватает данных";
      error = `Имя не может быть пустым`;
      return;
    }

    if (!botToken) {
      errorTitle = "Не хватает данных";
      error = `Токен не может быть пустым`;
      return;
    }

    isCreating = true;
    let tokenValidationError = getError(await validateBotToken(botToken));
    if (tokenValidationError !== null) {
      errorTitle = "Проверьте корректность токена";
      error = tokenValidationError;
      isCreating = false;
      return;
    }

    let botName = slugify(botDisplayName, {
      separator: "-",
      allowedChars: "a-zA-Z0-9-_",
      lowercase: true,
      trim: true,
    });
    const MAX_BOT_NAME_LEN = 64;
    const UUID_SUFFIX_LEN = 8;
    const MAX_TRANSLIT_PREFIX_LEN = MAX_BOT_NAME_LEN - UUID_SUFFIX_LEN - 1;
    if (botName.length > MAX_TRANSLIT_PREFIX_LEN) {
      botName = botName.slice(0, MAX_TRANSLIT_PREFIX_LEN);
    }
    botName += "-" + crypto.randomUUID().slice(0, UUID_SUFFIX_LEN);
    console.log("Generated bot name", botName);

    let newTokenSecretRes = await createBotTokenSecret(botName, botToken);
    let newTokenSaveErr = getError(newTokenSecretRes);
    if (newTokenSaveErr !== null) {
      errorTitle = "Не получилось сохранить токен";
      error = newTokenSaveErr;
      isCreating = false;
      return;
    }

    const config: BotConfig = {
      token_secret_name: unwrap(newTokenSecretRes),
      display_name: botDisplayName,
      user_flow_config: {
        entrypoints: [
          {
            command: {
              entrypoint_id: DEFAULT_START_COMMAND_ENTRYPOINT_ID,
              command: "start",
              short_description: "запустить бот",
              next_block_id: null,
            },
          },
        ],
        blocks: [],
        node_display_coords: Object.fromEntries([
          [DEFAULT_START_COMMAND_ENTRYPOINT_ID, { x: 0, y: 0 }],
          [BOT_INFO_NODE_ID, { x: 0, y: -150 }],
        ]),
      },
    };
    const res1 = await saveBotConfig(botName, config);
    isCreating = false;

    if (res1.ok) {
      error = null;
      const botInfo = unwrap(await getBotInfo(botName));
      newBotCallback(botName, botInfo);
      closePopup();
    } else if (!res1.ok) {
      errorTitle = "Ошибка сохранения";
      error = getError(res1);
    }
  }
</script>

<Flex direction="column" gap="md">
  <TextInput
    bind:value={botDisplayNameInput}
    error={userClickedCreate && !botDisplayNameInput}
    label="Имя"
    description="Это название бота в конструкторе. Его не увидят пользователь:ницы и его можно изменять."
    placeholder="Бот-волонтер"
  />
  <PasswordInput
    bind:value={botTokenInput}
    error={userClickedCreate && !botTokenInput}
    label="Токен"
    placeholder="123456789:ABCDEFGHIJKLMOPQRSTUVWXYZabcdefghij"
    description="Для создания бота: 
зайдите в Телеграм и через поиск найдите @BotFather;
введите команду /newbot;
дайте боту имя и @username;
скопируйте токен вашего бота из сообщения BotFather
    "
  />
  {#if error !== null}
    <ErrorBadge title={errorTitle || "Ошибка"} text={error} />
  {/if}
  <div class="save-button">
    <Button on:click={createNewBot} loading={isCreating}>Создать</Button>
  </div>
</Flex>
