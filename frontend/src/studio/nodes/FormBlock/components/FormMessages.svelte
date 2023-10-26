<script lang="ts">
  import { Accordion, Stack, Text } from "@svelteuidev/core";
  import type { FormMessages } from "../../../../api/types";
  import LocalizableTextInput from "../../../components/LocalizableTextInput.svelte";
  import { updateWithPrefilled } from "../prefill";
  import { languageConfigStore } from "../../../stores";
  import { validateLocalizableText } from "../../nodeValidators";
  import { formMessageName } from "../content";

  export let messages: FormMessages;

  messages = updateWithPrefilled(messages, $languageConfigStore);

  let openSections: string[] = [];
  for (const [key, msg] of Object.entries(messages)) {
    if (key !== "form_start" && !validateLocalizableText(msg, "", $languageConfigStore)) {
      openSections.push("technical");
      break;
    }
  }
</script>

<!-- TODO: hide most field under Advanced and fill with generic default values -->
<Stack>
  <LocalizableTextInput label={formMessageName("form_start")} bind:value={messages.form_start} />
  <Accordion multiple defaultValue={[]}>
    <Accordion.Item value="technical">
      <Text variant="link" slot="control">Технические</Text>
      <LocalizableTextInput label={formMessageName("field_is_skippable")} bind:value={messages.field_is_skippable} />
      <LocalizableTextInput
        label={formMessageName("field_is_not_skippable")}
        bind:value={messages.field_is_not_skippable}
      />
      <LocalizableTextInput
        label={formMessageName("please_enter_correct_value")}
        bind:value={messages.please_enter_correct_value}
      />
      <LocalizableTextInput label={formMessageName("unsupported_command")} bind:value={messages.unsupported_command} />
    </Accordion.Item>
  </Accordion>
</Stack>
