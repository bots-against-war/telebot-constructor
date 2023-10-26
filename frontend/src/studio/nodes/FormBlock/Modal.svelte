<script lang="ts">
  import { Tabs } from "@svelteuidev/core";
  import type { FormBlock } from "../../../api/types";
  import NodeModalControls from "../../components/NodeModalControls.svelte";

  import FormBranch from "./components/FormBranch.svelte";
  import FormMessages from "./components/FormMessages.svelte";
  import FormResultExportOptions from "./components/FormResultExportOptions.svelte";
  import type { FormErrorMessages, PrefillableFormErrorKey } from "./prefill";
  import { flattenedFormFields } from "../../../api/typeUtils";

  export let config: FormBlock;
  export let botName: string;
  export let onConfigUpdate: (newConfig: FormBlock) => any;

  function updateConfig() {
    config = editedConfig;
    onConfigUpdate(config);
  }

  let editedConfig: FormBlock = JSON.parse(JSON.stringify(config));
  let formErrorMessages: FormErrorMessages = {};
  $: {
    // extracting field-specific errors from individual fields to a global errors
    // object to be edited separately on messages tab
    const newErrorMessagesFromFields: FormErrorMessages = {};
    for (const fieldConfig of flattenedFormFields(editedConfig.members)) {
      if (fieldConfig.plain_text) {
        newErrorMessagesFromFields.empty_text_error_msg = fieldConfig.plain_text.empty_text_error_msg;
      } else if (fieldConfig.single_select) {
        newErrorMessagesFromFields.invalid_enum_error_msg = fieldConfig.single_select.invalid_enum_error_msg;
      }
    }
    // removing extra error keys (field type deleted -> key is not needed anymore)
    for (const existingKey in formErrorMessages) {
      if (!(existingKey in newErrorMessagesFromFields)) {
        // @ts-expect-error
        delete formErrorMessages[existingKey];
      }
    }
    // setting new keys on form error messages from fields
    formErrorMessages = { ...newErrorMessagesFromFields, ...formErrorMessages };
  }
</script>

<div>
  <h3>Форма</h3>
  <Tabs>
    <Tabs.Tab label={`Поля (${editedConfig.members.length})`}>
      <FormBranch bind:members={editedConfig.members} />
    </Tabs.Tab>
    <Tabs.Tab label="Сообщения">
      <FormMessages bind:messages={editedConfig.messages} bind:errors={formErrorMessages} />
    </Tabs.Tab>
    <Tabs.Tab label="Обработка результатов">
      <FormResultExportOptions bind:config={editedConfig.results_export} {botName} />
    </Tabs.Tab>
  </Tabs>
  <NodeModalControls on:save={updateConfig} />
</div>

<style>
</style>
