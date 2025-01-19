<script lang="ts">
  import { Button, Heading } from "flowbite-svelte";
  import Icon from "$frontend/components/icons/GridPlusColored.svelte";
</script>

<div class="flex flex-row justify-between">
  <Heading>Hello world!</Heading>
  <Button>Log in</Button>
</div>
<p class="text-red-500">Text example 1 2 3 4 5</p>
<Icon colors={["red", "green", "blue"]} />
