<script lang="ts">
  import { Button } from "flowbite-svelte";
  import { SvelteComponent } from "svelte";
  import type { Newable } from "ts-essentials";

  export let icon: Newable<SvelteComponent>;
  export let href: string | undefined = undefined;
  export let size: "xs" | "sm" | "lg" | "xl" | "md" = "xl";
  export let iconClass = "w-3 h-3 text-gray-700";
</script>

<Button
  {...$$restProps}
  pill
  outline
  class="!p-2 bg-none border-none hover:bg-gray-200"
  {size}
  on:click
  {href}
  target="_blank"
>
  <svelte:component this={icon} class={iconClass} />
</Button>
