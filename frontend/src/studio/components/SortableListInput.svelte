<script lang="ts">
  import { ActionIcon, CloseButton, Group, InputWrapper, Space, Stack } from "@svelteuidev/core";
  import { SortableList } from "@jhubbardsf/svelte-sortablejs";
  import { BarsOutline, PlusOutline } from "flowbite-svelte-icons";

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

<Stack>
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
          <Group override={{ padding: "5px 0" }}>
            <LocalizableTextInput bind:value={option.label} isLongText={false} />
            <div class="grip-handle">
              <Space w="md" />
              <BarsOutline />
            </div>
            <CloseButton
              on:click={() => {
                options = options.toSpliced(idx);
              }}
            />
          </Group>
        {/each}
      </SortableList>
    {/key}
    <ActionIcon
      on:click={() => {
        options = [...options, optionConstructor()];
      }}
    >
      <PlusOutline />
    </ActionIcon>
  </InputWrapper>
</Stack>

<style>
  .grip-handle {
    cursor: grab;
  }

  .grip-handle:active {
    cursor: grabbing;
  }
</style>
