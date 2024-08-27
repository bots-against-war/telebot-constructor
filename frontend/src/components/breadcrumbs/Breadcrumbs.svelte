<script lang="ts">
  import { Breadcrumb } from "flowbite-svelte";
  import Delimiter from "./Delimiter.svelte";
</script>

<div class="mb-2">
  <Breadcrumb>
    <slot />
    <Delimiter />
  </Breadcrumb>
</div>
