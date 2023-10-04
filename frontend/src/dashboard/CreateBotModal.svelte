<script lang="ts">
  import { saveBotConfig } from "../api/botConfig";
  import { Button, TextInput, Alert, Flex, PasswordInput } from "@svelteuidev/core";
  import { createBotTokenSecret, getError, getModalCloser, unwrap } from "../utils";
  import { slugify } from "transliteration";
  import { validateBotToken } from "../api/validation";
  import type { BotConfig } from "../api/types";

  export let newBotCallback: (botName: string, config: BotConfig) => void;

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

    const config = {
      token_secret_name: unwrap(newTokenSecretRes),
      display_name: botDisplayName,
      user_flow_config: {
        entrypoints: [],
        blocks: [],
        node_display_coords: {},
      },
    };
    const res = await saveBotConfig(botName, config);
    isCreating = false;

    console.log(res);

    if (res.ok) {
      error = null;
      newBotCallback(botName, config);
      closePopup();
    } else {
      errorTitle = "Ошибка сохранения";
      error = getError(res);
    }
  }
</script>

<Flex direction="column" gap="md">
  <TextInput
    bind:value={botDisplayNameInput}
    error={userClickedCreate && !botDisplayNameInput}
    label="Название"
    description="Не видно пользователь:ницам, только в конструкторе; можно изменить позже"
    placeholder="Бот-волонтер"
  />
  <PasswordInput
    bind:value={botTokenInput}
    error={userClickedCreate && !botTokenInput}
    label="Токен"
    placeholder="123456789:ABCDEFGHIJKLMOPQRSTUVWXYZabcdefghij"
    description="Можно изменить позже"
  />
  {#if error !== null}
    <Alert title={errorTitle || "Ошибка"} color="red">{error}</Alert>
  {/if}
  <div class="save-button">
    <Button on:click={createNewBot} loading={isCreating}>Создать</Button>
  </div>
</Flex>
