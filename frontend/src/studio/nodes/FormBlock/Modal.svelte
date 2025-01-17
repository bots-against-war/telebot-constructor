<script lang="ts">
  import { TabItem, Tabs } from "flowbite-svelte";
  import { locale, t } from "svelte-i18n";
  import { flattenedFormFields } from "../../../api/typeUtils";
  import type { FormBlock, FormBranchConfig } from "../../../api/types";
  import { TELEGRAM_MAX_MESSAGE_LENGTH_CHARS } from "../../../constants";
  import LocalizableTextInput from "../../components/LocalizableTextInput.svelte";
  import NodeModalBody from "../../components/NodeModalBody.svelte";
  import NodeModalControls from "../../components/NodeModalControls.svelte";
  import { languageConfigStore } from "../../stores";
  import { clone } from "../../utils";
  import { NODE_TITLE_KEY } from "../display";
  import FormBranch from "./components/FormBranch.svelte";
  import FormMessages from "./components/FormMessages.svelte";
  import FormResultExportOptions from "./components/FormResultExportOptions.svelte";
  import { getRandomFormStartMessage } from "./content";
  import { updatedWithPrefilled, type FormErrorMessages } from "./prefill";

  export let config: FormBlock;
  export let botId: string;
  export let onConfigUpdate: (newConfig: FormBlock) => any;

  function updateConfig() {
    editedConfig.members = topLevelBranch.members;

    editedConfig.messages = formMessages;
    // inserting global error values back into form fields
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
    formErrorMessages = updatedWithPrefilled(
      { ...newErrorMessagesFromFields, ...formErrorMessages },
      $languageConfigStore,
      $t,
      $locale,
    );
  }

  let formMessages = config.messages;
  formMessages = updatedWithPrefilled(formMessages, $languageConfigStore, $t, $locale);
</script>

<NodeModalBody title={$t(NODE_TITLE_KEY.form)}>
  <div slot="description" class="text-sm text-gray-600 mt-2">
    {$t("studio.form.ok_outcome_cond")} <strong>{$t("studio.form.ok_outcome")}</strong>.
    {@html $t("studio.form.cancel_outcome_cond")} <strong>{$t("studio.form.cancel_outcome")}</strong>.
  </div>
  <!-- NOTE: additional div is needed because Tabs have no top-level container -->
  <div>
    <Tabs style="underline" contentClass="mt-1">
      <TabItem open title={`${$t("studio.form.fields_tab")} (${flattenedFormFields(topLevelBranch.members).length})`}>
        <div class="mb-4">
          <LocalizableTextInput
            placeholder={getRandomFormStartMessage($t)}
            bind:value={formMessages.form_start}
            maxCharacters={TELEGRAM_MAX_MESSAGE_LENGTH_CHARS}
          />
        </div>
        <FormBranch isMovableUp={false} isMovableDown={false} bind:branch={topLevelBranch} />
      </TabItem>
      <TabItem title={$t("studio.form.answers_tab")}>
        <FormResultExportOptions bind:config={editedConfig.results_export} {botId} />
      </TabItem>
      <TabItem title={$t("studio.form.messages_tab")}>
        <FormMessages bind:messages={formMessages} bind:errors={formErrorMessages} />
      </TabItem>
    </Tabs>
  </div>
  <NodeModalControls on:save={updateConfig} />
</NodeModalBody>

<style>
</style>
