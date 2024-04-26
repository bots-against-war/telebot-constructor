<script lang="ts">
  import { Node } from "svelvet";
  import type { LanguageSelectBlock } from "../../../api/types";
  import Langauge from "../../../components/Language.svelte";
  import DataBadge from "../../../components/internal/DataBadge.svelte";
  import type { SvelvetPosition } from "../../../types";
  import { getModalOpener } from "../../../utils";
  import InputAnchor from "../../components/InputAnchor.svelte";
  import NodeContent from "../../components/NodeContent.svelte";
  import OutputAnchor from "../../components/OutputAnchor.svelte";
  import OutputAnchorsBox from "../../components/OutputAnchorsBox.svelte";
  import { NodeTypeKey } from "../display";
  import { DEFAULT_NODE_PROPS } from "../nodeProps";
  import { validateLanguageSelectBlock } from "../nodeValidators";
  import Modal from "./Modal.svelte";

  const openModal = getModalOpener();

  export let config: LanguageSelectBlock;
  export let position: SvelvetPosition;
  export let isValid = true;

  const setNewConfig = (newConfig: LanguageSelectBlock) => {
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
    key={NodeTypeKey.language_select}
    bind:isValid
    {config}
    clonable={false}
    configValidator={validateLanguageSelectBlock}
    on:delete
    on:clone
    on:edit={openEditModal}
  >
    <div class="flex flex-row gap-2">
      {#each config.supported_languages as language (language)}
        <DataBadge>
          <Langauge {language} />
        </DataBadge>
      {/each}
    </div>
  </NodeContent>
  <OutputAnchorsBox>
    <OutputAnchor bind:nextBlockId={config.next_block_id} />
    <OutputAnchor bind:nextBlockId={config.language_selected_next_block_id} anchorLabel="Выбран язык" />
  </OutputAnchorsBox>
</Node>
