<script lang="ts">
  import { Fileupload, Helper, Listgroup } from "flowbite-svelte";
  import type { Attachments, ContentBlock, ContentBlockContentAttachment } from "../../../api/types";
  import InputWrapper from "../../../components/inputs/InputWrapper.svelte";
  import { TELEGRAM_MAX_MESSAGE_LENGTH_CHARS } from "../../../constants";
  import LocalizableTextInput from "../../components/LocalizableTextInput.svelte";
  import NodeModalBody from "../../components/NodeModalBody.svelte";
  import NodeModalControls from "../../components/NodeModalControls.svelte";
  import { NODE_TITLE } from "../display";

  export let config: ContentBlock;
  export let onConfigUpdate: (newConfig: ContentBlock) => any;

  let editedMessageText = config.contents[0].text?.text || "";
  let files = initFiles(config.contents[0].attachments);

  async function updateConfig(): Promise<void> {
    const attachments = await serializeAttachments();
    config.contents = [{ text: { text: editedMessageText, markup: "markdown" }, attachments }];
    onConfigUpdate(config);
  }

  async function serializeAttachments(): Promise<Attachments> {
    const attachments: Attachments = [];

    if (!files) return attachments;

    for (let file of files) {
      // NOTE future improvement, add try catch block, err monitoring presence is required
      const image = await base64EncodeFileContent(file);
      const filename = file.name;
      attachments.push({ image, filename });
    }

    return attachments;
  }

  async function base64EncodeFileContent(file: File): Promise<string> {
    return new Promise<any>((resolve, reject) => {
      let reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () => reject(reader.error);

      reader.readAsDataURL(file);
    });
  }

  function decodeBase64(base64: string, filename: string) {
    const dataTypeMatch = base64.match(/data:(.+?);base64,/);
    if (!dataTypeMatch) throw "Failed to extract data type from base64 data URL";
    const type = dataTypeMatch[1];
    const [_, data] = base64.split(";base64,");
    const binary = atob(data);
    const uint8 = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; ++i) {
      uint8[i] = binary.charCodeAt(i);
    }

    const file = new File([uint8], filename, { type });
    return file;
  }

  function initFiles(attachments: Array<ContentBlockContentAttachment>): FileList | undefined {
    if (!attachments.length) return undefined;

    // NOTE DataTransfer is a hack, used to create a File List, which is required for a UI component
    const dataTransfer = new DataTransfer();
    attachments.forEach((obj) => {
      let { image, filename } = obj;

      if (typeof image !== "string" || typeof filename !== "string") return;

      const file = decodeBase64(image, filename);
      dataTransfer.items.add(file);
    });

    return dataTransfer.files;
  }

  let filenames: string[];
  $: {
    if (files) {
      filenames = [];
      for (const f of files) {
        filenames.push(f.name);
      }
    }
  }
</script>

<NodeModalBody title={NODE_TITLE.content}>
  <LocalizableTextInput
    label="Текст сообщения"
    bind:value={editedMessageText}
    maxCharacters={TELEGRAM_MAX_MESSAGE_LENGTH_CHARS}
    textareaRows={10}
    markdown
  />
  <InputWrapper label="Приложения" required={false}>
    <Fileupload id="multiple_files" class="mb-2" multiple bind:files accept="image/*" />
    <Helper>PNG, JPG, SVG, WEBP, GIF</Helper>
    {#if filenames}
      <Listgroup items={filenames} let:item class="mt-2">
        {#if item}
          {item}
        {/if}
      </Listgroup>
    {/if}
  </InputWrapper>
  <NodeModalControls on:save={updateConfig} />
</NodeModalBody>

<style>
</style>
