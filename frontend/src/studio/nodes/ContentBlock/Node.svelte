<script lang="ts">
  import { ImageSolid } from "flowbite-svelte-icons";
  import { Node } from "svelvet";
  import type { ContentBlock } from "../../../api/types";
  import type { SvelvetPosition } from "../../../types";
  import { getModalOpener } from "../../../utils";
  import InputAnchor from "../../components/InputAnchor.svelte";
  import LocalizableText from "../../components/LocalizableTextPreview.svelte";
  import NodeContent from "../../components/NodeContent.svelte";
  import OutputAnchor from "../../components/OutputAnchor.svelte";
  import OutputAnchorsBox from "../../components/OutputAnchorsBox.svelte";
  import { NodeTypeKey } from "../display";
  import { DEFAULT_NODE_PROPS } from "../nodeProps";
  import { validateContentBlock } from "../nodeValidators";
  import Modal from "./Modal.svelte";

  const openModal = getModalOpener();

  export let config: ContentBlock;
  export let position: SvelvetPosition;
  export let isValid = true;

  const setNewConfig = (newConfig: ContentBlock) => {
    config = newConfig;
  };
  const openEditModal = () =>
    openModal(Modal, {
      config,
      onConfigUpdate: setNewConfig,
    });
</script>

<Node id={config.block_id} bind:position {...DEFAULT_NODE_PROPS}>
  <InputAnchor />
  <NodeContent
    id={config.block_id}
    key={NodeTypeKey.content}
    {config}
    bind:isValid
    configValidator={validateContentBlock}
    on:delete
    on:clone
    on:edit={openEditModal}
  >
    {#if config.contents.length > 0 && config.contents[0].text}
      <div class="flex flex-row gap-2">
        {#if config.contents[0].attachments.length > 0}
          <ImageSolid color="gray" class="w-4 h-4" />
        {/if}
        <div class="w-full flex-grow">
          <LocalizableText text={config.contents[0].text?.text} maxHeightPx={80} />
        </div>
      </div>
    {/if}
  </NodeContent>
  <OutputAnchorsBox>
    <OutputAnchor bind:nextBlockId={config.next_block_id} />
  </OutputAnchorsBox>
</Node>
