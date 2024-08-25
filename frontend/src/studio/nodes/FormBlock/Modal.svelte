<script lang="ts">
  import { TabItem, Tabs } from "flowbite-svelte";
  import { flattenedFormFields } from "../../../api/typeUtils";
  import type { FormBlock, FormBranchConfig } from "../../../api/types";
  import LocalizableTextInput from "../../components/LocalizableTextInput.svelte";
  import NodeModalBody from "../../components/NodeModalBody.svelte";
  import NodeModalControls from "../../components/NodeModalControls.svelte";
  import { languageConfigStore } from "../../stores";
  import { clone } from "../../utils";
  import { NODE_TITLE } from "../display";
  import FormBranch from "./components/FormBranch.svelte";
  import FormMessages from "./components/FormMessages.svelte";
  import FormResultExportOptions from "./components/FormResultExportOptions.svelte";
  import { getRandomFormStartMessage } from "./content";
  import { updateWithPrefilled, type FormErrorMessages } from "./prefill";

  export let config: FormBlock;
  export let botId: string;
  export let onConfigUpdate: (newConfig: FormBlock) => any;

  function updateConfig() {
    editedConfig.members = topLevelBranch.members;
    // inserting global error values back into form fields

    console.log(editedConfig);
    console.log(formErrorMessages);
    for (const fieldConfig of flattenedFormFields(editedConfig.members)) {
      if (fieldConfig.plain_text) {
        fieldConfig.plain_text.empty_text_error_msg = formErrorMessages.empty_text_error_msg || "";
      } else if (fieldConfig.single_select) {
        fieldConfig.single_select.invalid_enum_error_msg = formErrorMessages.invalid_enum_error_msg || "";
      }
    }
    onConfigUpdate(editedConfig);
  }

  const editedConfig = clone(config);

  let topLevelBranch: FormBranchConfig = { members: editedConfig.members };

  // form error messages are reactive w.r.t. active fields
  // e.g. if no single-select field is present, single-select-specific errors are not needed
  // so, here we respond to changes in fields by changing error messages
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
    // also, prefilling it with default values for new keys
    [formErrorMessages] = updateWithPrefilled(
      { ...newErrorMessagesFromFields, ...formErrorMessages },
      $languageConfigStore,
    );
  }
</script>

<NodeModalBody title={NODE_TITLE.form}>
  <!-- NOTE: additional div is needed because Tabs have no top-level container -->
  <div>
    <Tabs style="underline" contentClass="mt-3">
      <TabItem open title={`Поля (${flattenedFormFields(topLevelBranch.members).length})`}>
        <div class="mb-4">
          <LocalizableTextInput
            placeholder={getRandomFormStartMessage()}
            bind:value={editedConfig.messages.form_start}
          />
        </div>
        <FormBranch isMovableUp={false} isMovableDown={false} bind:branch={topLevelBranch} />
      </TabItem>
      <TabItem title="Ответы">
        <FormResultExportOptions bind:config={editedConfig.results_export} {botId} blockId={config.block_id} />
      </TabItem>
      <TabItem title="Технические сообщения">
        <FormMessages bind:messages={editedConfig.messages} bind:errors={formErrorMessages} />
      </TabItem>
    </Tabs>
  </div>
  <NodeModalControls on:save={updateConfig} />
</NodeModalBody>

<style>
</style>
