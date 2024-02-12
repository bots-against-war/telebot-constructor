<script lang="ts">
  import { Accordion, AccordionItem } from "flowbite-svelte";
  import type { FormMessages } from "../../../../api/types";
  import LocalizableTextInput from "../../../components/LocalizableTextInput.svelte";
  import { languageConfigStore } from "../../../stores";
  import { validateLocalizableText } from "../../nodeValidators";
  import { formMessageName } from "../content";
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

  let openTechnical = false;
  $: {
    for (const [key, msg] of Object.entries(messages)) {
      if (key !== "form_start" && !validateLocalizableText(msg, "", $languageConfigStore)) {
        openTechnical = true;
        break;
      }
    }
  }
</script>

<Accordion multiple>
  <AccordionItem open>
    <span slot="header">Основное</span>
    <LocalizableTextInput label={formMessageName("form_start")} bind:value={messages.form_start} />
  </AccordionItem>

  <AccordionItem bind:open={openTechnical}>
    <span slot="header">Технические</span>
    {#each PREFILLABLE_FORM_MESSAGE_KEYS as key}
      <LocalizableTextInput label={formMessageName(key)} bind:value={messages[key]} />
    {/each}
  </AccordionItem>

  <AccordionItem disabled={Object.keys(errors).length === 0}>
    <span slot="header">Ошибки</span>
    {#each PREFILLABLE_FORM_ERROR_KEYS as key}
      {#if errors[key] !== undefined}
        <!-- no way to ignore this warning but it's ok -->
        <LocalizableTextInput label={formMessageName(key)} bind:value={errors[key]} />
      {/if}
    {/each}
  </AccordionItem>
</Accordion>
