<script lang="ts">
  import { NumberInput } from "@svelteuidev/core";

  export let label: string;
  export let groupChatId: number;
</script>

<NumberInput hideControls placeholder={label} {label} bind:value={groupChatId} />
