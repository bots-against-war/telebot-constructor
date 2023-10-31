<script lang="ts">
  import { Group } from "@svelteuidev/core";
  import { Node } from "svelvet";
  import OutputAnchorsBox from "../../components/OutputAnchorsBox.svelte";
  import Modal from "./Modal.svelte";
  import NodeContent from "../../components/NodeContent.svelte";
  import InputAnchor from "../../components/InputAnchor.svelte";
  import OutputAnchor from "../../components/OutputAnchor.svelte";
  import Langauge from "../../../components/Language.svelte";
  import DataBadge from "../../../components/internal/DataBadge.svelte";

  import type { SvelvetPosition } from "../../../types";
  import type { LanguageSelectBlock } from "../../../api/types";

  import { DEFAULT_NODE_PROPS } from "../nodeProps";
  import { HUE, headerColor } from "../colors";
  import { validateLanguageSelectBlock } from "../nodeValidators";
  import { getModalOpener } from "../../../utils";

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
    name="Выбор языка"
    headerColor={headerColor(HUE.language_select)}
    bind:isValid
    {config}
    configValidator={validateLanguageSelectBlock}
    on:delete
    on:edit={openEditModal}
  >
    <Group spacing="xs" override={{ maxWidth: "300px" }}>
      {#each config.supported_languages as language (language)}
        <DataBadge>
          <Langauge {language} />
        </DataBadge>
      {/each}
    </Group>
  </NodeContent>
  <OutputAnchorsBox>
    <OutputAnchor bind:nextBlockId={config.language_selected_next_block_id} />
  </OutputAnchorsBox>
</Node>
