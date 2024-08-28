<script lang="ts">
  import Centered from "./internal/Centered.svelte";
  import ErrorBadge from "./ErrorBadge.svelte";

  export let error: any;
  console.error("Fatal error: ", error);
</script>

<Centered>
  <ErrorBadge title="Fatal error" text={error} />
</Centered>
