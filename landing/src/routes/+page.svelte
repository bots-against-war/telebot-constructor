<script lang="ts">
  import { Button, Heading } from "flowbite-svelte";
  import Icon from "$frontend/components/icons/GridPlusColored.svelte";
  import PrimaryButton from "./PrimaryButton.svelte";
</script>

<!-- Header -->
<div class="flex flex-row justify-between items-center">
  <span>moduli</span>
  <PrimaryButton>Log in</PrimaryButton>
</div>
<div class="flex flex-row justify-between">
  <Heading class="font-header text-4xl font-extrabold">Hello world!</Heading>
</div>
<p class="text-red-500">Text example 1 2 3 4 5</p>
<Icon colors={["red", "green", "blue"]} />
