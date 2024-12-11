<script lang="ts">
  import { Button } from "flowbite-svelte";
  import { SvelteComponent } from "svelte";
  import type { Newable } from "ts-essentials";

  export let icon: Newable<SvelteComponent>;
  export let href: string | undefined = undefined;
  export let size: "xs" | "sm" | "lg" | "xl" | "md" = "xl";
  export let buttonClass = "!p-2 bg-none border-none hover:bg-gray-100";
  export let iconClass = "w-3 h-3 text-gray-700";
</script>

<Button {...$$restProps} outline class={buttonClass} {size} on:click on:keydown {href} target="_blank">
  <svelte:component this={icon} class={iconClass} />
  <slot />
</Button>
