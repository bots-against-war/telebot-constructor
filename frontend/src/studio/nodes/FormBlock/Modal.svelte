<script lang="ts">
  import { Tabs } from "@svelteuidev/core";
  import type { FormBlock, FormBranchConfig } from "../../../api/types";
  import NodeModalControls from "../../components/NodeModalControls.svelte";

  import FormBranch from "./components/FormBranch.svelte";
  import FormMessages from "./components/FormMessages.svelte";
  import FormResultExportOptions from "./components/FormResultExportOptions.svelte";
  import type { FormErrorMessages } from "./prefill";
  import { flattenedFormFields } from "../../../api/typeUtils";

  export let config: FormBlock;
  export let botName: string;
  export let onConfigUpdate: (newConfig: FormBlock) => any;

  function updateConfig() {
    config.members = topLevelBranch.members;
    // inserting global error values back into form fields
    for (const fieldConfig of flattenedFormFields(config.members)) {
      if (fieldConfig.plain_text) {
        fieldConfig.plain_text.empty_text_error_msg = formErrorMessages.empty_text_error_msg || "";
      } else if (fieldConfig.single_select) {
        fieldConfig.single_select.invalid_enum_error_msg = formErrorMessages.invalid_enum_error_msg || "";
      }
    }
    onConfigUpdate(config);
  }

  let topLevelBranch: FormBranchConfig = { members: config.members };

  let formErrorMessages: FormErrorMessages = {};
  $: {
    // extracting field-specific errors from individual fields to a global errors
    // object to be edited separately on messages tab
    const newErrorMessagesFromFields: FormErrorMessages = {};
    for (const fieldConfig of flattenedFormFields(topLevelBranch.members)) {
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
    <Tabs.Tab label={`Поля (${flattenedFormFields(topLevelBranch.members).length})`}>
      <FormBranch bind:branch={topLevelBranch} parentBranchMembers={[]} idxInParentBranch={0} />
    </Tabs.Tab>
    <Tabs.Tab label="Сообщения">
      <FormMessages bind:messages={config.messages} bind:errors={formErrorMessages} />
    </Tabs.Tab>
    <Tabs.Tab label="Обработка результатов">
      <FormResultExportOptions bind:config={config.results_export} {botName} />
    </Tabs.Tab>
  </Tabs>
  <NodeModalControls on:save={updateConfig} />
</div>

<style>
</style>
