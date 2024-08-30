<script lang="ts">
  import { SortableList } from "@jhubbardsf/svelte-sortablejs";
  import { BarsOutline, CloseOutline, PlusOutline } from "flowbite-svelte-icons";
  import ActionIcon from "../../components/ActionIcon.svelte";
  import InputWrapper from "../../components/inputs/InputWrapper.svelte";
  import { type LocalizableText } from "../../types";
  import LocalizableTextInput from "./LocalizableTextInput.svelte";

  interface Option {
    label: LocalizableText;
    [k: string]: unknown;
  }

  export let label: string;
  export let options: Option[];
  export let optionConstructor: () => Option;
  let forceUpdateCounter = 0;

  const generateId = () => `sortable-list-item-${crypto.randomUUID()}`;
  let optionsWithIds = options.map((o) => {
    return { option: o, id: generateId() };
  });
  const optionWithIdConstructor = () => {
    return { option: optionConstructor(), id: generateId() };
  };
  $: {
    options = optionsWithIds.map(({ option }) => option);
  }

  export let selectedLang: string | null = null;
</script>

<InputWrapper {label}>
  {#key forceUpdateCounter}
    <SortableList
      class="sortable-class-unused"
      handle=".grip-handle"
      onSort={(e) => {
        const itemsCopy = [...optionsWithIds];
        console.debug(`Moving option, before: ${JSON.stringify(itemsCopy)}`);
        const moved = itemsCopy.splice(e.oldIndex, 1)[0];
        itemsCopy.splice(e.newIndex, 0, moved);
        console.debug(`... after: ${JSON.stringify(itemsCopy)}`);
        optionsWithIds = itemsCopy;
        forceUpdateCounter += 1;
      }}
    >
      {#each optionsWithIds as item, idx (item.id)}
        <div class="flex flex-row gap-1 items-center">
          <LocalizableTextInput bind:value={item.option.label} isLongText={false} {selectedLang} />
          <div class="grip-handle">
            <BarsOutline class="w-4 h-4 text-gray-700" />
          </div>
          <ActionIcon
            icon={CloseOutline}
            iconClass="w-4 h-4 text-gray-700"
            on:click={() => {
              optionsWithIds = optionsWithIds.toSpliced(idx, 1);
            }}
          />
        </div>
      {/each}
    </SortableList>
  {/key}
  <ActionIcon
    icon={PlusOutline}
    on:click={() => {
      optionsWithIds = [...optionsWithIds, optionWithIdConstructor()];
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
