<script lang="ts">
  import { onMount } from "svelte";
  import type { Attachments, ContentBlock, ContentBlockContentAttachment, Image } from "../../../api/types";
  import LocalizableTextInput from "../../components/LocalizableTextInput.svelte";
  import { Fileupload, Label, Listgroup, ListgroupItem } from "flowbite-svelte";
  import NodeModalBody from "../../components/NodeModalBody.svelte";
  import NodeModalControls from "../../components/NodeModalControls.svelte";
  import { NODE_TITLE } from "../display";

  export let config: ContentBlock;
  export let onConfigUpdate: (newConfig: ContentBlock) => any;

  let editedMessageText = config.contents[0].text?.text || "";
  let files: FileList;

  async function updateConfig(): Promise<void> {
    const attachments = await serializeAttachments();
    config.contents = [{ text: { text: editedMessageText, markup: "none" }, attachments }];
    onConfigUpdate(config);
  }

  async function serializeAttachments(): Promise<Attachments> {
    const attachments: Attachments = [];

    if (files.length === 0) return attachments;

    // TODO Replace string for multiple files once backend is ready
    // for (let i = 0; i < files.length; ++i) {
    for (let i = 0; i < 1; ++i) {
      const file = files[i];

      try {
        const image = await readFile(file);
        const name = file.name;
        attachments.push({ image, name });
      } catch (err) {
        console.error(err);
      }
    }

    return attachments;
  }

  async function readFile(file: File): Promise<any> {
    return new Promise<any>((resolve, reject) => {
      let reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () => reject(reader.error);

      reader.readAsDataURL(file);
    });
  }

  function decodeBase64(base64: string, name: string) {
    const [type, data] = base64.split(";base64,");
    const binary = atob(data);
    const uint8 = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; ++i) {
      uint8[i] = binary.charCodeAt(i);
    }

    const file = new File([uint8], name, { type });
    return file;
  }

  onMount(() => {
    const attachments = config.contents[0].attachments;
    if (!attachments.length) return;

    const dataTransfer = new DataTransfer();
    attachments.forEach((obj) => {
      let { image, name } = obj;

      if (typeof image !== "string") return;

      const file = decodeBase64(image, name);
      dataTransfer.items.add(file);
    });
    files = dataTransfer.files;
  });
</script>

<NodeModalBody title={NODE_TITLE.content}>
  <LocalizableTextInput label="Текст сообщения" bind:value={editedMessageText} />

  <Label class="pb-2" for="multiple_files">Upload multiple files</Label>
  <Fileupload id="multiple_files" multiple bind:files />
  <Listgroup items={files} let:item class="mt-2">
    {#if item}
      {item.name}
    {:else}
      <ListgroupItem>No files</ListgroupItem>
    {/if}
  </Listgroup>

  <NodeModalControls on:save={updateConfig} />
</NodeModalBody>

<style>
</style>
