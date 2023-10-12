<script lang="ts">
  import { PasswordInput, Stack, Button, Group } from "@svelteuidev/core";

  import { validateBotToken } from "../../api/validation";
  import { createBotTokenSecret, getError, getModalCloser } from "../../utils";

  const closeModal = getModalCloser();

  export let botName: string;
  export let onNewTokenSecretName: (newTokenSecretName: string) => any;

  let newBotTokenInput = "";
  let isUpdating = false;
  let userClickedUpdate = false;
  let errorTitle: string | null = null;
  let error: string | null = null;

  async function saveNewBotToken() {
    userClickedUpdate = true;
    let botToken = newBotTokenInput.trim();

    if (!botToken) {
      errorTitle = "Не хватает данных";
      error = `Токен не может быть пустым`;
      return;
    }

    isUpdating = true;
    const tokenValidationError = getError(await validateBotToken(botToken));
    if (tokenValidationError !== null) {
      errorTitle = "Проверьте корректность токена";
      error = tokenValidationError;
      isUpdating = false;
      return;
    }

    const newTokenSecretRes = await createBotTokenSecret(botName, botToken);
    if (!newTokenSecretRes.ok) {
      errorTitle = "Не получилось сохранить токен";
      error = newTokenSecretRes.error;
      isUpdating = false;
      return;
    }

    onNewTokenSecretName(newTokenSecretRes.data);
    closeModal();
  }
</script>

<Stack spacing="lg">
  <PasswordInput
    bind:value={newBotTokenInput}
    error={userClickedUpdate && !newBotTokenInput}
    label="Токен нового бота"
    placeholder="123456789:ABCDEFGHIJKLMOPQRSTUVWXYZabcdefghij"
  />

  <Group>
    <Button loading={isUpdating} on:click={saveNewBotToken}>Обновить бота</Button>
    <Button variant="outline" on:click={closeModal}>Отмена</Button>
  </Group>
</Stack>
