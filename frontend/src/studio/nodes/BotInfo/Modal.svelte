<script lang="ts">
  import { Group, Image, Input, Stack, Text, Textarea, Title } from "@svelteuidev/core";
  import { QuestionCircleOutline } from "flowbite-svelte-icons";

  import type { TgBotUser } from "../../../api/types";
  import { base64Image } from "../../../studio/utils";
  import { updateBotUser } from "../../../api/botUser";
  import ErrorBadge from "../../../components/ErrorBadge.svelte";
  import { getModalCloser } from "../../../utils";
  import NodeModalControls from "../../components/NodeModalControls.svelte";

  const closeModal = getModalCloser();

  export let botName: string;
  export let botUser: TgBotUser;
  export let onBotUserUpdated: (updated: TgBotUser) => any;

  let isUpdating = false;
  let updateError: string | null = null;

  async function saveBotUser() {
    isUpdating = true;
    const res = await updateBotUser(botName, {
      name: botUser.name,
      description: botUser.description,
      short_description: botUser.short_description,
    });
    isUpdating = false;
    if (res.ok) {
      onBotUserUpdated(botUser);
      closeModal();
    } else {
      updateError = res.error;
    }
  }
</script>

<Stack spacing="lg">
  <Group>
    <Image
      src={botUser.userpic !== null ? base64Image(botUser.userpic) : null}
      radius={1000}
      width={100}
      height={100}
      usePlaceholder
    >
      <svelte:fragment slot="placeholder">
        <QuestionCircleOutline />
      </svelte:fragment>
    </Image>
    <Stack>
      <Title>
        <Input bind:value={botUser.name} />
      </Title>
      <Text color="dimmed">@{botUser.username}</Text>
    </Stack>
  </Group>
  <Textarea
    label="О себе"
    description="Текст в профиле бота"
    required={false}
    resize="vertical"
    bind:value={botUser.short_description}
  />
  <Textarea
    label="Что может делать этот бот?"
    description="Текст для новых пользовательниц, перед командой /start"
    required={false}
    resize="vertical"
    bind:value={botUser.description}
  />
  {#if updateError !== null}
    <ErrorBadge title="Ошибка сохранения деталей бота" text={updateError} />
  {/if}
  <NodeModalControls on:save={saveBotUser} />
</Stack>
