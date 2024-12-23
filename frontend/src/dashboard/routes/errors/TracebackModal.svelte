<script lang="ts">
  import { Heading } from "flowbite-svelte";

  export let traceback: string;
</script>

<Heading tag="h3" class="mb-3">Exception traceback</Heading>
<p class="whitespace-pre border-gray-400 border-2 bg-gray-300 w-fit py-2">
  {traceback}
</p>
