<script lang="ts">
  import { BreadcrumbItem } from "flowbite-svelte";
  import { type BotInfo } from "../../api/types";
  import { dashboardPath } from "../../routeUtils";
  import Delimiter from "./Delimiter.svelte";

  export let botInfo: BotInfo;
</script>

<BreadcrumbItem href={dashboardPath(botInfo.bot_id)}>
  <svelte:fragment slot="icon">
    <Delimiter />
  </svelte:fragment>
  {botInfo.display_name}
</BreadcrumbItem>
