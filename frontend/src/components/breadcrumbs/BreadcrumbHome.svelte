<script>
  import { _ } from "svelte-i18n";
  import { BreadcrumbItem } from "flowbite-svelte";
  import { botListingPath } from "../../routeUtils";
</script>

<BreadcrumbItem home href={botListingPath()}>
  <div slot="icon"></div>
  {$_("listing.title")}
</BreadcrumbItem>
