<script lang="ts">
  import { t } from "svelte-i18n";
  import { Button, Heading } from "flowbite-svelte";
  import { navigate } from "svelte-routing";
  import { deleteBotConfig } from "../../../api/botConfig";
  import { stopBot } from "../../../api/lifecycle";
  import { type BotInfo } from "../../../api/types";
  import BreadcrumbDashboard from "../../../components/breadcrumbs/BreadcrumbDashboard.svelte";
  import BreadcrumbHome from "../../../components/breadcrumbs/BreadcrumbHome.svelte";
  import Breadcrumbs from "../../../components/breadcrumbs/Breadcrumbs.svelte";
  import Navbar from "../../../components/Navbar.svelte";
  import Page from "../../../components/Page.svelte";
  import PageContent from "../../../components/PageContent.svelte";
  import { botListingPath, dashboardPath } from "../../../routeUtils";
  import { withConfirmation } from "../../../utils";

  export let botInfo: BotInfo;

  const stopRunningBot = withConfirmation(
    $t("dashboard.confirm_stop_bot"),
    async () => {
      stopBot(botInfo.bot_id);
      navigate(dashboardPath(botInfo.bot_id));
    },
    $t("dashboard.stop_bot"),
  );

  const deleteBot = withConfirmation(
    $t("dashboard.confirm_delete_bot"),
    async () => {
      deleteBotConfig(botInfo.bot_id);
      navigate(botListingPath());
    },
    $t("dashboard.delete_bot"),
  );
</script>

<Page>
  <Navbar />
  <PageContent>
    <Breadcrumbs>
      <BreadcrumbHome />
      <BreadcrumbDashboard {botInfo} />
    </Breadcrumbs>
    <Heading tag="h3">{$t("dashboard.settings")}</Heading>
    <div class="mt-4 flex flex-col gap-3 w-fit">
      <Button color="red" size="xl" outline on:click={stopRunningBot} disabled={botInfo.running_version === null}>
        {$t("dashboard.stop_bot")}
      </Button>
      <Button color="red" size="xl" outline on:click={deleteBot}>{$t("dashboard.delete_bot")}</Button>
    </div>
  </PageContent>
</Page>
