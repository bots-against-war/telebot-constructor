<script lang="ts">
  import { SortableList } from "@jhubbardsf/svelte-sortablejs";
  // import { ActionIcon, CloseButton, Group, InputWrapper, Space, Stack } from "@svelteuidev/core";

  import InputWrapper from "../../components/inputs/InputWrapper.svelte";
  import ActionIcon from "../../components/ActionIcon.svelte";
  import { BarsOutline, PlusOutline, CloseOutline } from "flowbite-svelte-icons";

  import LocalizableTextInput from "./LocalizableTextInput.svelte";

  import { type LocalizableText } from "../../types";

  interface SortableListItem {
    label: LocalizableText;
    [k: string]: unknown;
  }

  export let label: string;
  export let options: SortableListItem[];
  export let optionConstructor: () => SortableListItem;
  let optionsListResortedCount: number = 0;
</script>

<div>
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
          <div class="flex flex-row py-1 gap-1 items-baseline">
            <LocalizableTextInput bind:value={option.label} isLongText={false} />
            <div class="grip-handle">
              <BarsOutline />
            </div>
            <ActionIcon
              icon={CloseOutline}
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
</div>

<style>
  .grip-handle {
    cursor: grab;
  }

  .grip-handle:active {
    cursor: grabbing;
  }
</style>
