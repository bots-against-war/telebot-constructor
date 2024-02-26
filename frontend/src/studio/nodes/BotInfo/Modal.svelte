<script lang="ts">
  import { Avatar } from "flowbite-svelte";
  import { updateBotUser } from "../../../api/botUser";
  import type { TgBotUser } from "../../../api/types";
  import ErrorBadge from "../../../components/ErrorBadge.svelte";
  import Textarea from "../../../components/inputs/Textarea.svelte";
  import TextInput from "../../../components/inputs/TextInput.svelte";
  import { base64Image } from "../../../studio/utils";
  import { getModalCloser } from "../../../utils";
  import NodeModalBody from "../../components/NodeModalBody.svelte";
  import NodeModalControls from "../../components/NodeModalControls.svelte";

  const closeModal = getModalCloser();

  export let botName: string;
  export let botUser: TgBotUser;
  export let onBotUserUpdated: (updated: TgBotUser) => any;

  let isUpdating = false;
  let updateError: string | null = null;
  const MAX_BOT_NAME_LEN: number = 64;
  const MAX_BOT_SHORT_DESCRIPTION_LEN: number = 120;
  const MAX_BOT_DESCRIPTION_LEN: number = 512;

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

<NodeModalBody>
  <div class="flex flex-row gap-2 items-center">
    <Avatar src={botUser.userpic ? base64Image(botUser.userpic) : undefined} class="w-20 h-20" />
    <div class="h-full w-full flex flex-col gap-1">
      <TextInput styleClass="text-2xl" bind:value={botUser.name} maxLength={MAX_BOT_NAME_LEN} />
      <p class="text-gray-500">@{botUser.username}</p>
    </div>
  </div>
  <Textarea label="О себе" description="Текст в профиле бота" required={false} bind:value={botUser.short_description} maxLength={MAX_BOT_SHORT_DESCRIPTION_LEN} />
  <Textarea
    label="Что может делать этот бот?"
    description="Текст для новых пользовательниц, перед командой /start"
    required={false}
    bind:value={botUser.description}
    maxLength={MAX_BOT_DESCRIPTION_LEN}
  />
  {#if updateError !== null}
    <ErrorBadge title="Ошибка сохранения деталей бота" text={updateError} />
  {/if}
  <NodeModalControls on:save={saveBotUser} autoClose={false} />
</NodeModalBody>
