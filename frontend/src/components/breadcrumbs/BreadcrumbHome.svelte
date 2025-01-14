<script>
  import { BreadcrumbItem } from "flowbite-svelte";
  import { t } from "svelte-i18n";
  import { botListingPath } from "../../routeUtils";
</script>

<BreadcrumbItem home href={botListingPath()}>
  <div slot="icon"></div>
  {$t("listing.title")}
</BreadcrumbItem>
