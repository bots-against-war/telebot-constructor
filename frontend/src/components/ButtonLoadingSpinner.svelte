<script lang="ts">
  import { Spinner } from "flowbite-svelte";

  export let loading = false;
</script>

{#if loading}
  <Spinner class="me-3" size="4" color="white" />
{/if}
