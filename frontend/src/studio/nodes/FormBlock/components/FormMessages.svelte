<script lang="ts">
  import { t } from "svelte-i18n";
  import type { FormMessages } from "../../../../api/types";
  import { TELEGRAM_MAX_MESSAGE_LENGTH_CHARS } from "../../../../constants";
  import LocalizableTextInput from "../../../components/LocalizableTextInput.svelte";
  import { languageConfigStore } from "../../../stores";
  import { formMessageDescription, formMessageName } from "../content";
  import {
    PREFILLABLE_FORM_ERROR_KEYS,
    PREFILLABLE_FORM_MESSAGE_KEYS,
    updateWithPrefilled,
    type FormErrorMessages,
  } from "../prefill";

  export let messages: FormMessages;
  export let errors: FormErrorMessages;

  [messages] = updateWithPrefilled(messages, $languageConfigStore);
  [errors] = updateWithPrefilled(errors, $languageConfigStore);
</script>

<div class="flex flex-col gap-1">
  <h2 class="font-bold mb-2">{$t("studio.form.errors")}</h2>
  {#each PREFILLABLE_FORM_ERROR_KEYS as key (key)}
    {#if errors[key]}
      <!-- no way to ignore this error but it should be ok -->
      <LocalizableTextInput
        label={formMessageName(key, $t)}
        description={formMessageDescription(key, $t)}
        bind:value={errors[key]}
        maxCharacters={TELEGRAM_MAX_MESSAGE_LENGTH_CHARS / 2}
      />
    {/if}
  {/each}
</div>

<div class="mt-3 pt-3 border-t-2 flex flex-col gap-1">
  <h2 class="font-bold mb-2">{$t("studio.form.technical_messages")}</h2>
  {#each PREFILLABLE_FORM_MESSAGE_KEYS as key (key)}
    <LocalizableTextInput
      label={formMessageName(key, $t)}
      description={formMessageDescription(key, $t)}
      bind:value={messages[key]}
      maxCharacters={TELEGRAM_MAX_MESSAGE_LENGTH_CHARS / 2}
    />
  {/each}
</div>
