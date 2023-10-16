<script lang="ts">
  import { Alert } from "@svelteuidev/core";
  import { ExclamationTriangle } from "radix-icons-svelte";

  export let title: string | undefined = undefined;
  export let text: string;
</script>

<Alert color="red" {title} icon={ExclamationTriangle}>
  {text}
</Alert>
