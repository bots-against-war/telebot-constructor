<script lang="ts">
  import { Li, List } from "flowbite-svelte";
  import { Node } from "svelvet";
  import { flattenedFormFields } from "../../../api/typeUtils";
  import { type FormBlock } from "../../../api/types";
  import type { SvelvetPosition } from "../../../types";
  import { getModalOpener } from "../../../utils";
  import InputAnchor from "../../components/InputAnchor.svelte";
  import LocalizableText from "../../components/LocalizableTextPreview.svelte";
  import NodeContent from "../../components/NodeContent.svelte";
  import OutputAnchor from "../../components/OutputAnchor.svelte";
  import OutputAnchorsBox from "../../components/OutputAnchorsBox.svelte";
  import { NodeTypeKey } from "../display";
  import { DEFAULT_NODE_PROPS } from "../nodeProps";
  import { validateFormBlock } from "../nodeValidators";
  import Modal from "./Modal.svelte";
  import { getBaseFormFieldConfig } from "./utils";

  const openModal = getModalOpener();

  export let config: FormBlock;
  export let position: SvelvetPosition;
  export let isValid = true;
  export let botId: string;

  const setNewConfig = (newConfig: FormBlock) => {
    config = newConfig;
  };
  const openEditModal = () =>
    openModal(Modal, {
      config,
      botId,
      onConfigUpdate: setNewConfig,
    });
</script>

<Node id={config.block_id} bind:position {...DEFAULT_NODE_PROPS}>
  <InputAnchor />
  <NodeContent
    id={config.block_id}
    key={NodeTypeKey.form}
    {config}
    configValidator={validateFormBlock}
    bind:isValid
    on:delete
    on:clone
    on:edit={openEditModal}
  >
    <div class="flex flex-col">
      <LocalizableText text={config.messages.form_start} maxHeightPx={80} />
      <List>
        {#each flattenedFormFields(config.members) as field}
          <Li>{getBaseFormFieldConfig(field).name}</Li>
        {/each}
      </List>
    </div>
  </NodeContent>
  <OutputAnchorsBox>
    <OutputAnchor bind:nextBlockId={config.form_completed_next_block_id} anchorLabel="ОК" />
    <OutputAnchor bind:nextBlockId={config.form_cancelled_next_block_id} anchorLabel="Отмена" />
  </OutputAnchorsBox>
</Node>
