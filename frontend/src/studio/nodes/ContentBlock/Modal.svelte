<script lang="ts">
  import { Dropzone, Fileupload, Helper, Listgroup } from "flowbite-svelte";
  import type { Attachments, ContentBlock, ContentBlockContentAttachment } from "../../../api/types";
  import InputWrapper from "../../../components/inputs/InputWrapper.svelte";
  import { TELEGRAM_MAX_CAPTION_LENGTH_CHARS, TELEGRAM_MAX_MESSAGE_LENGTH_CHARS } from "../../../constants";
  import LocalizableTextInput from "../../components/LocalizableTextInput.svelte";
  import NodeModalBody from "../../components/NodeModalBody.svelte";
  import NodeModalControls from "../../components/NodeModalControls.svelte";
  import { NODE_TITLE } from "../display";

  export let config: ContentBlock;
  export let onConfigUpdate: (newConfig: ContentBlock) => any;

  let messageText = config.contents.length > 0 ? config.contents[0].text?.text || "" : "";
  let attachments = config.contents.length > 0 ? config.contents[0].attachments : [];

  async function updateConfig(): Promise<void> {
    config.contents = [{ text: { text: messageText, markup: "markdown" }, attachments }];
    onConfigUpdate(config);
  }

  let isUploadingFiles = false;

  function uploadFiles(files: FileList) {
    // set uploading flag
    // upload files one by one, collect errors, if occur
    // add media ids to the list of attachments
    // notify of errors, if occured
    // reset uploading flag
  }

  function handleDropFile(event: DragEvent): any {
    event.preventDefault();
    if (event.dataTransfer === null) return;
    uploadFiles(event.dataTransfer.files);
  }

  function handleSelectFile(event: Event): any {
    if (!(event.target instanceof HTMLInputElement)) return;
    if (event.target.files === null) return;
    uploadFiles(event.target.files);
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
  <Dropzone
    id="dropzone"
    on:drop={handleDropFile}
    on:dragover={(event) => event.preventDefault()}
    on:change={handleSelectFile}
  >
    <!-- TODO: use icon from icon pack -->
    <svg
      aria-hidden="true"
      class="mb-3 w-10 h-10 text-gray-400"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
      ><path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
      /></svg
    >
    <!-- TODO: render existing attachments as images with crosses to delete -->
    <!-- {#if value.length === 0}
      <p class="mb-2 text-sm text-gray-500 dark:text-gray-400">
        <span class="font-semibold">Click to upload</span> or drag and drop
      </p>
      <p class="text-xs text-gray-500 dark:text-gray-400">SVG, PNG, JPG or GIF (MAX. 800x400px)</p>
    {:else}
      <p>{showFiles(value)}</p>
    {/if} -->
  </Dropzone>
  <NodeModalControls on:save={updateConfig} />
</NodeModalBody>
