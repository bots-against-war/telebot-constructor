<script lang="ts">
  import { Button } from "flowbite-svelte";
  import { SvelteComponent } from "svelte";
  import type { Newable } from "ts-essentials";

  export let icon: Newable<SvelteComponent>;
  export let href: string | undefined = undefined;
</script>

<Button pill outline class="!p-2 bg-none border-none hover:bg-gray-300" size="xl" on:click {href} target="_blank">
  <svelte:component this={icon} class="w-3 h-3 text-gray-700" />
</Button>
