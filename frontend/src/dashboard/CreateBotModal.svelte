<script lang="ts">
  import { Button, Li, List, Spinner } from "flowbite-svelte";
  import { slugify } from "transliteration";
  import { saveBotConfig } from "../api/botConfig";
  import { getBotInfo } from "../api/botInfo";
  import type { BotConfig, BotInfo } from "../api/types";
  import { validateBotToken } from "../api/validation";
  import ErrorBadge from "../components/ErrorBadge.svelte";
  import PasswordInput from "../components/inputs/PasswordInput.svelte";
  import TextInput from "../components/inputs/TextInput.svelte";
  import { BOT_INFO_NODE_ID, DEFAULT_START_COMMAND_ENTRYPOINT_ID } from "../constants";
  import { createBotTokenSecret, getError, getModalCloser, unwrap } from "../utils";
  import ButtonLoadingSpinner from "../components/ButtonLoadingSpinner.svelte";

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
    if (!botDisplayName || !botToken) {
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
              short_description: "начало работы",
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
    const res1 = await saveBotConfig(botName, { config, start: false, version_message: null });
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

<div class="flex flex-col gap-4">
  <TextInput
    bind:value={botDisplayNameInput}
    error={userClickedCreate && !botDisplayNameInput ? "Имя бота не может быть пустым" : null}
    label="Имя"
    description="Это название бота в конструкторе. Его не увидят пользователь:ницы и его можно изменять."
    placeholder="Бот-волонтер"
  />
  <PasswordInput
    bind:value={botTokenInput}
    error={userClickedCreate && !botTokenInput ? "Токен не может быть пустым" : null}
    label="Токен"
    placeholder="123456789:ABCDEFGHIJKLMOPQRSTUVWXYZabcdefghij"
  >
    <svelte:fragment slot="description">
      <p>Для создания бота:</p>
      <List class="mb-2 marker:text-gray-600">
        <Li>зайдите в Телеграм и через поиск найдите @BotFather</Li>
        <Li>введите команду /newbot</Li>
        <Li>дайте боту имя и @username</Li>
        <Li>скопируйте токен вашего бота из сообщения BotFather</Li>
      </List>
    </svelte:fragment>
  </PasswordInput>
  {#if error !== null}
    <ErrorBadge title={errorTitle || "Ошибка"} text={error} />
  {/if}
  <div class="save-button">
    <Button on:click={createNewBot}>
      <ButtonLoadingSpinner loading={isCreating} />
      Создать
    </Button>
  </div>
</div>
