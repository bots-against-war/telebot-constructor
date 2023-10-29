<script lang="ts">
  import { Stack, Group, ActionIcon, InputWrapper, CloseButton } from "@svelteuidev/core";
  import { SortableList } from "@jhubbardsf/svelte-sortablejs";
  import { DragHandleDots2, Plus } from "radix-icons-svelte";
  import type { SingleSelectFormFieldConfig } from "../../../../api/types";
  import LocalizableTextInput from "../../../components/LocalizableTextInput.svelte";

  export let config: SingleSelectFormFieldConfig;
  let optionsListResortedCount: number = 0;
</script>

<Stack>
  <InputWrapper label="Варианты">
    {#key optionsListResortedCount}
      <SortableList
        class="sortable-class-unused"
        handle=".grip-handle"
        onSort={(e) => {
          const optionsCopy = [...config.options];
          console.debug(`Moving option, before: ${JSON.stringify(optionsCopy)}`);
          const moved = optionsCopy.splice(e.oldIndex, 1)[0];
          optionsCopy.splice(e.newIndex, 0, moved);
          console.debug(`... after: ${JSON.stringify(optionsCopy)}`);
          config.options = optionsCopy;
          optionsListResortedCount += 1;
        }}
      >
        {#each config.options as option, idx}
          <Group override={{ padding: "5px 0" }}>
            <LocalizableTextInput bind:value={option.label} isLongText={false} />
            <div class="grip-handle">
              <DragHandleDots2 />
            </div>
            <CloseButton
              on:click={() => {
                config.options = config.options.toSpliced(idx);
              }}
            />
          </Group>
        {/each}
      </SortableList>
    {/key}
    <ActionIcon
      on:click={() => {
        config.options = [...config.options, { id: `opt-${crypto.randomUUID()}`, label: "" }];
      }}
    >
      <Plus />
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
