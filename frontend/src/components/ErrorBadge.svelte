<script lang="ts">
  import { Alert } from "@svelteuidev/core";
  import { ExclamationCircleOutline } from "flowbite-svelte-icons";

  export let title: string | undefined = undefined;
  export let text: string;
</script>

<Alert color="red" {title} icon={ExclamationCircleOutline}>
  {text}
</Alert>
