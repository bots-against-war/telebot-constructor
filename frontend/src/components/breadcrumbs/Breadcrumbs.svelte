<script lang="ts">
  import { Breadcrumb } from "flowbite-svelte";
  import Delimiter from "./Delimiter.svelte";
</script>

<Breadcrumb>
  <slot />
  <Delimiter />
</Breadcrumb>
