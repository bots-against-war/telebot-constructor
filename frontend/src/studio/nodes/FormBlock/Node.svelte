<script lang="ts">
  import { Node } from "svelvet";
  import Modal from "./Modal.svelte";
  import NodeContent from "../../components/NodeContent.svelte";
  import InputAnchor from "../../components/InputAnchor.svelte";
  import OutputAnchor from "../../components/OutputAnchor.svelte";
  import OutputAnchorsBox from "../../components/OutputAnchorsBox.svelte";

  import { DEFAULT_NODE_PROPS } from "../nodeProps";
  import { NodeTypeKey } from "../display";
  import { type FormBlock } from "../../../api/types";
  import type { SvelvetPosition } from "../../../types";
  import { getModalOpener } from "../../../utils";
  import { validateFormBlock } from "../nodeValidators";
  import { flattenedFormFields } from "../../../api/typeUtils";

  const openModal = getModalOpener();

  export let config: FormBlock;
  export let position: SvelvetPosition;
  export let isValid = true;
  export let botName: string;

  const setNewConfig = (newConfig: FormBlock) => {
    config = newConfig;
  };
  const openEditModal = () =>
    openModal(Modal, {
      config,
      botName,
      onConfigUpdate: setNewConfig,
    });
</script>

<Node id={config.block_id} bind:position {...DEFAULT_NODE_PROPS}>
  <InputAnchor />
  <NodeContent
    key={NodeTypeKey.form}
    {config}
    configValidator={validateFormBlock}
    bind:isValid
    on:delete
    on:edit={openEditModal}
  >
    Полей: {flattenedFormFields(config.members).length}
  </NodeContent>
  <OutputAnchorsBox>
    <OutputAnchor bind:nextBlockId={config.form_completed_next_block_id} anchorLabel="ОК" />
    <OutputAnchor bind:nextBlockId={config.form_cancelled_next_block_id} anchorLabel="Отмена" />
  </OutputAnchorsBox>
</Node>
