<script lang="ts">
  import { A, Card } from "flowbite-svelte";

  export let title: string | undefined = undefined;
  export let moreLinkHref: string | undefined = undefined;
  export let moreLinkTitle: string | undefined = undefined;
</script>

<Card padding="sm" class="text-inherit" size="xl">
  {#if title}
    <h2 class="text-lg font-bold text-gray-900 pb-2">{title}</h2>
  {/if}
  <slot />
  {#if moreLinkHref && moreLinkTitle}
    <div class="mt-3">
      <A href={moreLinkHref}>{moreLinkTitle}</A>
    </div>
  {/if}
</Card>
