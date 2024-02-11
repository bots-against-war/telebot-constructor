<script lang="ts">
  import { Label } from "flowbite-svelte";

  export let label: string;
  export let description: string | null = null;
  export let error: string | boolean | null = null;
</script>

<Label class="block space-y-1">
  <span class="font-bold">{label}</span>
  <div class=" text-gray-600">
    <slot name="description">
      {#if description !== null}
        <p>
          {description}
        </p>
      {/if}
    </slot>
  </div>
  <slot />
  {#if typeof error == "string"}
    <p class=" text-red-600">{error}</p>
  {/if}
</Label>
