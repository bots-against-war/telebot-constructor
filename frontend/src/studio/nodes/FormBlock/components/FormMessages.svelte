<script lang="ts">
  import { Accordion, Text } from "@svelteuidev/core";
  import type { FormMessages } from "../../../../api/types";
  import LocalizableTextInput from "../../../components/LocalizableTextInput.svelte";
  import {
    updateWithPrefilled,
    type FormErrorMessages,
    PREFILLABLE_FORM_ERROR_KEYS,
    PREFILLABLE_FORM_MESSAGE_KEYS,
  } from "../prefill";
  import { languageConfigStore } from "../../../stores";
  import { validateLocalizableText } from "../../nodeValidators";
  import { formMessageName } from "../content";

  export let messages: FormMessages;
  export let errors: FormErrorMessages;

  [messages] = updateWithPrefilled(messages, $languageConfigStore);
  $: {
    // reactivity block is required because errors are mutated from outside the component
    // so, we need to re-prefill them each time
    [errors] = updateWithPrefilled(errors, $languageConfigStore);
  }

  let openSections: string[] = ["main"];
  $: {
    for (const [key, msg] of Object.entries(messages)) {
      if (key !== "form_start" && !validateLocalizableText(msg, "", $languageConfigStore)) {
        openSections.push("technical");
        break;
      }
    }
  }
</script>

<Accordion multiple defaultValue={openSections} variant="contained">
  <Accordion.Item value="main">
    <Text slot="control">Основное</Text>
    <LocalizableTextInput label={formMessageName("form_start")} bind:value={messages.form_start} />
  </Accordion.Item>

  <Accordion.Item value="technical">
    <Text slot="control">Технические</Text>
    {#each PREFILLABLE_FORM_MESSAGE_KEYS as key}
      <LocalizableTextInput label={formMessageName(key)} bind:value={messages[key]} />
    {/each}
  </Accordion.Item>

  <Accordion.Item value="errors" disabled={Object.keys(errors).length === 0}>
    <Text slot="control">Ошибки</Text>
    {#each PREFILLABLE_FORM_ERROR_KEYS as key}
      {#if errors[key] !== undefined}
        <!-- no way to ignore this warning but it's ok -->
        <LocalizableTextInput label={formMessageName(key)} bind:value={errors[key]} />
      {/if}
    {/each}
  </Accordion.Item>
</Accordion>
