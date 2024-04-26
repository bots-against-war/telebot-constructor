<script lang="ts">
  import { ChevronDownOutline, ChevronUpOutline, CloseOutline } from "flowbite-svelte-icons";
  import { createEventDispatcher } from "svelte";
  import ActionIcon from "../../../../components/ActionIcon.svelte";

  const dispatch = createEventDispatcher<{ delete: null; moveup: null; movedown: null }>();

  export let isMovableDown: boolean;
  export let isMovableUp: boolean;
  export let isDeletable: boolean;

  const iconClass = "w-3 h-3 text-gray-500";
</script>

<div>
  <div class="w-full flex flex-row gap-1 justify-start mb-1">
    {#if isMovableUp}
      <ActionIcon {iconClass} size="sm" icon={ChevronUpOutline} on:click={() => dispatch("moveup")} />
    {/if}
    {#if isMovableDown}
      <ActionIcon {iconClass} size="sm" icon={ChevronDownOutline} on:click={() => dispatch("movedown")} />
    {/if}
    {#if isDeletable}
      <ActionIcon {iconClass} size="sm" icon={CloseOutline} on:click={() => dispatch("delete")} />
    {/if}
  </div>
  <slot />
</div>
