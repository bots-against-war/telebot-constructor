<script lang="ts">
  import { A, Button, Li, List } from "flowbite-svelte";
  import { t } from "svelte-i18n";
  import { navigate } from "svelte-routing";
  import { slugify } from "transliteration";
  import { saveBotConfig } from "../api/botConfig";
  import type { BotConfig } from "../api/types";
  import { validateBotToken } from "../api/validation";
  import ErrorBadge from "../components/AlertBadge.svelte";
  import ButtonLoadingSpinner from "../components/ButtonLoadingSpinner.svelte";
  import PasswordInput from "../components/inputs/PasswordInput.svelte";
  import TextInput from "../components/inputs/TextInput.svelte";
  import { BOT_INFO_NODE_ID, DEFAULT_START_COMMAND_ENTRYPOINT_ID } from "../constants";
  import { dashboardPath } from "../routeUtils";
  import { createBotTokenSecret, getError, getModalCloser, unwrap } from "../utils";

  const closeModal = getModalCloser();

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
      errorTitle = $t("listing.newbot.incorrect_token_error");
      error = tokenValidationError;
      isCreating = false;
      return;
    }

    let botId = slugify(botDisplayName, {
      separator: "-",
      allowedChars: "a-zA-Z0-9-_",
      lowercase: true,
      trim: true,
    });
    const MAX_BOT_ID_LEN = 64;
    const UUID_SUFFIX_LEN = 8;
    const MAX_TRANSLIT_PREFIX_LEN = MAX_BOT_ID_LEN - UUID_SUFFIX_LEN - 1;
    if (botId.length > MAX_TRANSLIT_PREFIX_LEN) {
      botId = botId.slice(0, MAX_TRANSLIT_PREFIX_LEN);
    }
    botId += "-" + crypto.randomUUID().slice(0, UUID_SUFFIX_LEN);
    console.debug("Generated bot id", botId);

    let newTokenSecretRes = await createBotTokenSecret(botId, botToken);
    let newTokenSaveErr = getError(newTokenSecretRes);
    if (newTokenSaveErr !== null) {
      errorTitle = $t("listing.newbot.failed_to_save_token_error");
      error = newTokenSaveErr;
      isCreating = false;
      return;
    }

    const config: BotConfig = {
      token_secret_name: unwrap(newTokenSecretRes),
      user_flow_config: {
        entrypoints: [
          {
            command: {
              entrypoint_id: DEFAULT_START_COMMAND_ENTRYPOINT_ID,
              command: "start",
              short_description: $t("listing.newbot.start_cmd_description"),
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
    const res1 = await saveBotConfig(botId, {
      config,
      start: false,
      version_message: null,
      display_name: botDisplayName,
    });

    if (res1.ok) {
      error = null;
      navigate(dashboardPath(botId));
      closeModal();
    } else if (!res1.ok) {
      isCreating = false;
      errorTitle = $t("listing.newbot.generic_saving_error");
      error = getError(res1);
    }
  }
</script>

<div class="flex flex-col gap-4">
  <TextInput
    bind:value={botDisplayNameInput}
    label={$t("listing.newbot.botname")}
    description={$t("listing.newbot.botname_description")}
    placeholder={$t("listing.newbot.botname_placeholder")}
    error={userClickedCreate && !botDisplayNameInput ? $t("listing.newbot.bot_name_cannot_be_empty_error") : null}
  />
  <PasswordInput
    bind:value={botTokenInput}
    label={$t("listing.newbot.token")}
    error={userClickedCreate && !botTokenInput ? $t("listing.newbot.token_cannot_be_empty_error") : null}
    placeholder="123456789:ABCDEFGHIJKLMOPQRSTUVWXYZabcdefghij"
  >
    <svelte:fragment slot="description">
      <p>{$t("listing.newbot.howto.p1")}</p>
      <List class="mb-2 marker:text-gray-600">
        <Li>{$t("listing.newbot.howto.p2")} <A href="https://t.me/BotFather">@BotFather</A></Li>
        <Li>{$t("listing.newbot.howto.p3")} <code>/newbot</code></Li>
        <Li>{$t("listing.newbot.howto.p4")}</Li>
        <Li>{$t("listing.newbot.howto.p5")}</Li>
      </List>
    </svelte:fragment>
  </PasswordInput>
  {#if error !== null}
    <ErrorBadge title={errorTitle || $t("listing.newbot.generic_error")} text={error} />
  {/if}
  <div>
    <Button on:click={createNewBot}>
      <ButtonLoadingSpinner loading={isCreating} />
      {$t("listing.create")}
    </Button>
    <Button outline on:click={closeModal}>{$t("generic.cancel")}</Button>
  </div>
</div>
