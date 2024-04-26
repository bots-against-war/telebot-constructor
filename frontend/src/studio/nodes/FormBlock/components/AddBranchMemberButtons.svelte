<script lang="ts">
  import { Button } from "flowbite-svelte";
  import { PlusOutline } from "flowbite-svelte-icons";
  import { type ButtonProps } from "flowbite-svelte/Button.svelte";
  import { createEventDispatcher } from "svelte";
  import type { SingleSelectFormFieldConfig } from "../../../../api/types";

  export let allowAddField: boolean;
  export let currentSwitchField: SingleSelectFormFieldConfig | null | undefined;

  const dispatch = createEventDispatcher<{ add_field: null; add_branch: null }>();

  const buttonProps: ButtonProps = {
    color: "light",
    size: "xs",
    outline: true,
    class: "px-4 py-2 border-none hover:bg-gray-200",
  };

  let currentSwitchFieldName: string | null = null;
  $: {
    if (currentSwitchField) {
      currentSwitchFieldName = currentSwitchField.name;
    }
  }
</script>

<div class="flex flex-row justify-center gap-2">
  {#if allowAddField}
    <Button on:click={() => dispatch("add_field")} {...buttonProps}>
      <PlusOutline size="xs" class="mr-2" />
      Поле
    </Button>
  {/if}
  {#if currentSwitchField}
    <Button on:click={() => dispatch("add_branch")} {...buttonProps}>
      <PlusOutline size="xs" class="mr-2" />
      <span>
        Ветвь с условием
        {#if currentSwitchFieldName}
          на "{currentSwitchFieldName}"
        {/if}
      </span>
    </Button>
  {/if}
  {#if !allowAddField && !currentSwitchField}
    <!-- just a spacer -->
    <div class="h-4" />
  {/if}
</div>
