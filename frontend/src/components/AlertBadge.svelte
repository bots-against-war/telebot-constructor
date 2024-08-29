<script lang="ts">
  import { Alert, Li, List } from "flowbite-svelte";
  import { ExclamationCircleOutline } from "flowbite-svelte-icons";

  export let title: string | undefined = undefined;
  export let text: string | string[];
  export let color: "red" | "yellow" = "red";
</script>

<Alert {color}>
  <ExclamationCircleOutline slot="icon" class="w-5 h-5 self-start p-0" />
  <div>
    {#if title}
      <strong class="text-lg block mt-[-0.25rem]">{title}</strong>
    {/if}
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
  </div>
</Alert>
