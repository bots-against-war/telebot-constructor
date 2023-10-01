<script lang="ts">
  import { Button, type ButtonProps } from "@svelteuidev/core";

  // target is forcefully set to empty string for client-side routing to work
  // see https://github.com/EmilTholin/svelte-routing/issues/260

  type $$Props = ButtonProps;
</script>

<Button target="" {...$$restProps}><slot /></Button>
