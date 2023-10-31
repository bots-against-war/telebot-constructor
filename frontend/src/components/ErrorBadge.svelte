<script lang="ts">
  import { Alert } from "@svelteuidev/core";
  import { ExclamationTriangle } from "radix-icons-svelte";

  export let title: string | undefined = undefined;
  export let text: string | string[];
</script>

<Alert color="red" {title} icon={ExclamationTriangle}>
  {#if typeof text === "string"}
    {text}
  {:else}
    <ul class="condensed-list">
      {#each text as textItem}
        <li>{textItem}</li>
      {/each}
    </ul>
  {/if}
</Alert>

<style>
  ul.condensed-list {
    padding-inline-start: 13px;
    margin: 0;
  }
</style>
