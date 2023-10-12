<script lang="ts">
  import { Node } from "svelvet";

  import type { SvelvetPosition } from "../../../types";
  import type { LanguageSelectBlock } from "../../../api/types";
  import { getModalOpener } from "../../../utils";

  import Modal from "./Modal.svelte";
  import NodeContent from "../../components/NodeContent.svelte";
  import InputAnchor from "../../components/InputAnchor.svelte";
  import { DEFAULT_NODE_PROPS } from "../nodeProps";
  import { HUE, headerColor } from "../colors";

  const openModal = getModalOpener();

  export let config: LanguageSelectBlock;
  export let position: SvelvetPosition;

  const setNewConfig = (newConfig: LanguageSelectBlock) => {
    config = newConfig;
    console.log("HO config updated");
    console.log(config);
  };
</script>

<Node id={config.block_id} bind:position {...DEFAULT_NODE_PROPS}>
  <InputAnchor />
  <NodeContent
    name="Выбор языка"
    headerColor={headerColor(HUE.language_select)}
    on:delete
    on:edit={() =>
      openModal(Modal, {
        config,
        onConfigUpdate: setNewConfig,
      })}
  ></NodeContent>
</Node>
