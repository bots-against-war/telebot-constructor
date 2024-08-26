<script>
  import { BreadcrumbItem } from "flowbite-svelte";
  import { botListingPath } from "../../routeUtils";
</script>

<BreadcrumbItem home href={botListingPath()}>
  <div slot="icon"></div>
  Мои боты
</BreadcrumbItem>
