<script lang="ts">
  import { SortableList } from "@jhubbardsf/svelte-sortablejs";
  import { BarsOutline, CloseOutline, PlusOutline } from "flowbite-svelte-icons";
  import ActionIcon from "../../components/ActionIcon.svelte";
  import InputWrapper from "../../components/inputs/InputWrapper.svelte";
  import { type LocalizableText } from "../../types";
  import LocalizableTextInput from "./LocalizableTextInput.svelte";

  interface SortableListItem {
    label: LocalizableText;
    [k: string]: unknown;
  }

  export let label: string;
  export let options: SortableListItem[];
  export let optionConstructor: () => SortableListItem;
  let optionsListResortedCount: number = 0;

  export let selectedLang: string | null = null;
</script>

<InputWrapper {label}>
  {#key optionsListResortedCount}
    <SortableList
      class="sortable-class-unused"
      handle=".grip-handle"
      onSort={(e) => {
        const optionsCopy = [...options];
        console.debug(`Moving option, before: ${JSON.stringify(optionsCopy)}`);
        const moved = optionsCopy.splice(e.oldIndex, 1)[0];
        optionsCopy.splice(e.newIndex, 0, moved);
        console.debug(`... after: ${JSON.stringify(optionsCopy)}`);
        options = optionsCopy;
        optionsListResortedCount += 1;
      }}
    >
      {#each options as option, idx}
        <div class="flex flex-row gap-1 items-center">
          <LocalizableTextInput bind:value={option.label} isLongText={false} {selectedLang} />
          <div class="grip-handle">
            <BarsOutline class="w-4 h-4 text-gray-700" />
          </div>
          <ActionIcon
            icon={CloseOutline}
            iconClass="w-4 h-4 text-gray-700"
            on:click={() => {
              options = options.toSpliced(idx);
            }}
          />
        </div>
      {/each}
    </SortableList>
  {/key}
  <ActionIcon
    icon={PlusOutline}
    on:click={() => {
      options = [...options, optionConstructor()];
    }}
  />
</InputWrapper>

<style>
  .grip-handle {
    cursor: grab;
  }

  .grip-handle:active {
    cursor: grabbing;
  }
</style>
