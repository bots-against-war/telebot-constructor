<script lang="ts">
  import { Spinner } from "flowbite-svelte";
  import { saveMedia } from "../../../api/media";
  import type { ContentBlock } from "../../../api/types";
  import AlertBadge from "../../../components/AlertBadge.svelte";
  import InputWrapper from "../../../components/inputs/InputWrapper.svelte";
  import { TELEGRAM_MAX_CAPTION_LENGTH_CHARS, TELEGRAM_MAX_MESSAGE_LENGTH_CHARS } from "../../../constants";
  import LocalizableTextInput from "../../components/LocalizableTextInput.svelte";
  import NodeModalBody from "../../components/NodeModalBody.svelte";
  import NodeModalControls from "../../components/NodeModalControls.svelte";
  import { NODE_TITLE } from "../display";
  import Attachment from "./Attachment.svelte";
  import UploadFileButton from "./UploadFileButton.svelte";

  export let botId: string;
  export let config: ContentBlock;
  export let onConfigUpdate: (newConfig: ContentBlock) => any;

  let messageText = config.contents.length > 0 ? config.contents[0].text?.text || "" : "";
  let attachments = config.contents.length > 0 ? config.contents[0].attachments : [];

  async function updateConfig(): Promise<void> {
    config.contents = [{ text: { text: messageText, markup: "markdown" }, attachments }];
    onConfigUpdate(config);
  }

  let isUploadingFiles = false;

  async function handleSelectFile(event: Event): Promise<any> {
    if (!(event.target instanceof HTMLInputElement)) return;
    if (event.target.files === null) return;
    if (event.target.files.length != 1) return;
    isUploadingFiles = true;
    try {
      const file = event.target.files[0];
      const saveMediaResult = await saveMedia(file, botId);
      if (!saveMediaResult.ok) {
        window.alert(saveMediaResult.error);
        return;
      }
      attachments = [...attachments, { image: saveMediaResult.data }];
    } catch (e) {
      console.error(e);
      window.alert("Unexpected error uploading file");
    } finally {
      isUploadingFiles = false;
    }
  }

  function deleteAttachment(mediaId: string) {
    attachments = attachments.filter((a) => a.image != mediaId);
  }
</script>

<NodeModalBody title={NODE_TITLE.content}>
  <LocalizableTextInput
    label="Текст сообщения"
    bind:value={messageText}
    maxCharacters={attachments.length > 0 ? TELEGRAM_MAX_CAPTION_LENGTH_CHARS : TELEGRAM_MAX_MESSAGE_LENGTH_CHARS}
    textareaRows={10}
    markdown
    required={false}
  />
  <InputWrapper label="Приложения" required={false}>
    <div class="flex flex-row gap-3 flex-wrap items-center">
      {#each attachments as attachment (attachment.image)}
        {#if attachment.image}
          <Attachment {botId} mediaId={attachment.image} on:delete={(e) => deleteAttachment(e.detail)} />
        {:else}
          <AlertBadge text="Unexpected attachment data" />
        {/if}
      {/each}
      {#if isUploadingFiles}
        <Spinner />
      {/if}
      <UploadFileButton on:change={handleSelectFile} disabled={isUploadingFiles} />
    </div>
  </InputWrapper>
  <NodeModalControls on:save={updateConfig} />
</NodeModalBody>
