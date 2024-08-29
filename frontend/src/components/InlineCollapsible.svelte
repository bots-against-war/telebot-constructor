<script lang="ts">
  import { ArrowLeftOutline, ArrowRightOutline } from "flowbite-svelte-icons";

  export let closedIcon = ArrowRightOutline;
  export let openIcon = ArrowLeftOutline;

  let isCollapsed = true;
</script>

<span>
  <slot />
  {#if isCollapsed}
    <button
      on:click={() => {
        isCollapsed = false;
      }}
      class="h-4 ms-1"><svelte:component this={closedIcon} /></button
    >
  {:else}
    <slot name="expanded" />
    <button
      on:click={() => {
        isCollapsed = true;
      }}
      class="h-4"><svelte:component this={openIcon} /></button
    >
  {/if}
</span>
