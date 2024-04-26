<script lang="ts">
  import { ChevronDownOutline, ChevronUpOutline, CloseOutline } from "flowbite-svelte-icons";
  import { createEventDispatcher } from "svelte";
  import ActionIcon from "../../../../components/ActionIcon.svelte";

  const dispatch = createEventDispatcher<{ delete: null; moveup: null; movedown: null }>();

  export let isMovableDown: boolean;
  export let isMovableUp: boolean;
  export let isDeletable: boolean;

  const iconClass = "w-3 h-3 text-gray-500";
  const buttonClass = "!p-1 bg-none border-none hover:bg-gray-200";
</script>

<div class="relative mt-[10px]">
  <div class="w-fit absolute right-0 bottom-full">
    {#if isMovableUp || isMovableDown || isDeletable}
      <div class="px-2 py-1 bg-white border-t border-x rounded-tr-md rounded-tl-md">
        {#if isMovableUp}
          <ActionIcon {iconClass} {buttonClass} size="sm" icon={ChevronUpOutline} on:click={() => dispatch("moveup")} />
        {/if}
        {#if isMovableDown}
          <ActionIcon
            {iconClass}
            {buttonClass}
            size="sm"
            icon={ChevronDownOutline}
            on:click={() => dispatch("movedown")}
          />
        {/if}
        {#if isDeletable}
          <ActionIcon {iconClass} {buttonClass} size="sm" icon={CloseOutline} on:click={() => dispatch("delete")} />
        {/if}
      </div>
    {/if}
  </div>
  <slot />
</div>
