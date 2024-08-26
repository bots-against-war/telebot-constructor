<script lang="ts">
  import { Label } from "flowbite-svelte";

  export let label: string | null;
  export let description: string | null = null;
  export let error: string | boolean | null = null;
  export let required: boolean = true;

  const inputId = crypto.randomUUID().slice(0, 16);
</script>

<Label class="block space-y-1" for={inputId}>
  {#if label}
    <span class="font-bold">{label}</span>
    {#if required}
      <span class="ml-1 text-red-700 font-bold">*</span>
    {/if}
  {/if}
  {#if $$slots.description}
    <div class="text-gray-600">
      <slot name="description" />
    </div>
  {:else if description !== null}
    <p class="text-gray-600">
      {description}
    </p>
  {/if}
  <slot {inputId} />
  {#if typeof error == "string"}
    <p class="text-red-600">{error}</p>
  {/if}
</Label>
