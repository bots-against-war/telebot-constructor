<script lang="ts">
  import { Node } from "svelvet";
  import Modal from "./Modal.svelte";
  import NodeContent from "../../components/NodeContent.svelte";
  import InputAnchor from "../../components/InputAnchor.svelte";
  import OutputAnchor from "../../components/OutputAnchor.svelte";
  import OutputAnchorsBox from "../../components/OutputAnchorsBox.svelte";

  import { DEFAULT_NODE_PROPS } from "../nodeProps";
  import { HUE, headerColor } from "../colors";
  import { type FormBlock } from "../../../api/types";
  import type { SvelvetPosition } from "../../../types";
  import { getModalOpener } from "../../../utils";

  const openModal = getModalOpener();

  export let config: FormBlock;
  export let position: SvelvetPosition;
  export let isValid = true;

  const setNewConfig = (newConfig: FormBlock) => {
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
  <NodeContent name="Форма" headerColor={headerColor(HUE.form)} bind:isValid on:delete on:edit={openEditModal}>
    <!-- TODO add node content validation -->
    TBD
  </NodeContent>
  <OutputAnchorsBox>
    <OutputAnchor bind:nextBlockId={config.form_completed_next_block_id} anchorLabel="ОК" />
    <OutputAnchor bind:nextBlockId={config.form_completed_next_block_id} anchorLabel="Отмена" />
  </OutputAnchorsBox>
</Node>
