<script lang="ts">
  import type { FormMessages } from "../../../../api/types";
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
  <h2 class="font-bold mb-2">Ошибки</h2>
  {#each PREFILLABLE_FORM_ERROR_KEYS as key (key)}
    {#if errors[key]}
      <!-- no way to ignore this error but it should be ok -->
      <LocalizableTextInput
        label={formMessageName(key)}
        description={formMessageDescription(key)}
        bind:value={errors[key]}
      />
    {/if}
  {/each}
</div>

<div class="mt-3 pt-3 border-t-2 flex flex-col gap-1">
  <h2 class="font-bold mb-2">Технические сообщения</h2>
  {#each PREFILLABLE_FORM_MESSAGE_KEYS as key (key)}
    <LocalizableTextInput
      label={formMessageName(key)}
      description={formMessageDescription(key)}
      bind:value={messages[key]}
    />
  {/each}
</div>
