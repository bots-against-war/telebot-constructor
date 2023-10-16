<script lang="ts">
  import { Node } from "svelvet";
  import type { ContentBlock } from "../../../api/types";
  import NodeContent from "../../components/NodeContent.svelte";
  import OutputAnchor from "../../components/OutputAnchor.svelte";
  import InputAnchor from "../../components/InputAnchor.svelte";
  import type { SvelvetPosition } from "../../../types";

  import Modal from "./Modal.svelte";
  import { getModalOpener } from "../../../utils";
  import { DEFAULT_NODE_PROPS } from "../nodeProps";
  import { HUE, headerColor } from "../colors";
  import { validateContentBlock } from "../nodeValidators";
  import LocalizableText from "../../components/LocalizableText.svelte";
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
    name="Контент"
    headerColor={headerColor(HUE.content)}
    {config}
    bind:isValid
    configValidator={validateContentBlock}
    on:delete
    on:edit={openEditModal}
  >
    {#if config.contents.length > 0 && config.contents[0].text}
      <LocalizableText text={config.contents[0].text?.text} />
    {/if}
  </NodeContent>
  <OutputAnchor bind:nextBlockId={config.next_block_id} />
</Node>
