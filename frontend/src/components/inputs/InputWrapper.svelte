<script lang="ts">
  import { Label } from "flowbite-svelte";

  export let label: string | undefined;
  export let description: string | null = null;
  export let error: string | boolean | null = null;
  export let required: boolean = true;
</script>

<Label class="block space-y-1">
  {#if label}
    <span class="font-bold">{label}</span>
    {#if required}
      <span class="ml-1 text-red-700 font-bold">*</span>
    {/if}
  {/if}
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
