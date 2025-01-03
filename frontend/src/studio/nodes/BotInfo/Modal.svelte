<script lang="ts">
  import { t } from "svelte-i18n";
  import { Avatar } from "flowbite-svelte";
  import { getBotUser, updateBotUser } from "../../../api/botUser";
  import type { TgBotUser } from "../../../api/types";
  import ErrorBadge from "../../../components/AlertBadge.svelte";
  import Textarea from "../../../components/inputs/Textarea.svelte";
  import TextInput from "../../../components/inputs/TextInput.svelte";
  import LoadingScreen from "../../../components/LoadingScreen.svelte";
  import { base64Image } from "../../../studio/utils";
  import { getModalCloser, unwrap } from "../../../utils";
  import NodeModalBody from "../../components/NodeModalBody.svelte";
  import NodeModalControls from "../../components/NodeModalControls.svelte";

  const closeModal = getModalCloser();

  export let botId: string;
  export let onBotUserUpdated: (updated: TgBotUser) => any;

  let botUser: TgBotUser | null = null;
  const loadBotUser = async () => {
    const loaded = unwrap(await getBotUser(botId));
    botUser = loaded;
    onBotUserUpdated(loaded);
  };

  let isUpdating = false;
  let updateError: string | null = null;
  const MAX_BOT_ID_LEN = 64;
  const MAX_BOT_SHORT_DESCRIPTION_LEN = 120;
  const MAX_BOT_DESCRIPTION_LEN = 512;

  async function saveBotUser() {
    if (botUser === null) return;
    isUpdating = true;
    const res = await updateBotUser(botId, {
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
  {#await loadBotUser()}
    <LoadingScreen />
  {:then}
    {#if botUser !== null}
      <div class="flex flex-row gap-2 items-center">
        <Avatar src={botUser.userpic ? base64Image(botUser.userpic) : undefined} class="w-20 h-20" />
        <div class="h-full w-full flex flex-col gap-1">
          <TextInput styleClass="text-2xl" bind:value={botUser.name} maxLength={MAX_BOT_ID_LEN} />
          <p class="text-gray-500">@{botUser.username}</p>
        </div>
      </div>
      <Textarea
        label={$t("studio.info.about_label")}
        description={$t("studio.info.about_descr")}
        required={false}
        bind:value={botUser.short_description}
        maxLength={MAX_BOT_SHORT_DESCRIPTION_LEN}
        preventExceedingMaxLength
      />
      <Textarea
        label={$t("studio.info.what_this_bot_can_do_label")}
        description={$t("studio.info.what_this_bot_can_do_descr")}
        required={false}
        bind:value={botUser.description}
        maxLength={MAX_BOT_DESCRIPTION_LEN}
        preventExceedingMaxLength
      />
      {#if updateError !== null}
        <ErrorBadge title={$t("studio.info.error_saving_bot_info")} text={updateError} />
      {/if}
      <ErrorBadge color="yellow" text={$t("studio.info.changes_are_immediate")} />
      <NodeModalControls on:save={saveBotUser} autoClose={false} />
    {:else}
      <ErrorBadge title="Unexpected error" text="Unexpected error" />
    {/if}
  {:catch e}
    <ErrorBadge title={$t("components.bot_user_badge.data_loading_error")} text={e} />
  {/await}
</NodeModalBody>
