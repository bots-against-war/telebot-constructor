<script lang="ts">
  import { Alert, Li, List } from "flowbite-svelte";
  import { ExclamationCircleOutline } from "flowbite-svelte-icons";

  export let title: string | undefined = undefined;
  export let text: string | string[];
</script>

<Alert color="red" {title}>
  <ExclamationCircleOutline slot="icon" class="w-4 h-4 self-start p-0" />
  {#if typeof text === "string"}
    {text}
  {:else if Symbol.iterator in Object(text)}
    <List>
      {#each text as textItem}
        <Li>{textItem}</Li>
      {/each}
    </List>
  {:else}
    {text}
  {/if}
</Alert>
