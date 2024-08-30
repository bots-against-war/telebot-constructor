<script lang="ts">
  import { Heading } from "flowbite-svelte";

  export let title: string | undefined = undefined;
</script>

<div class="flex flex-col gap-4">
  {#if title}
    <div>
      <Heading tag="h4">{title}</Heading>
      <slot name="description" />
    </div>
  {/if}
  <slot />
</div>
