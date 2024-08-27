<script lang="ts">
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
  console.log(botInfo);

  const stopRunningBot = withConfirmation(
    "Вы уверены что хотите бота? Он перестанет реагировать на команды и отвечать " +
      "пользователь:ницам! Запустить его можно будет в любой момент " +
      "из конструктора или истории версий.",
    async () => {
      stopBot(botInfo.bot_id);
      navigate(dashboardPath(botInfo.bot_id));
    },
    "Остановить",
  );

  const deleteBot = withConfirmation(
    "Вы уверены, что хотите удалить бота? Это действие дельзя отменить!",
    async () => {
      deleteBotConfig(botInfo.bot_id);
      navigate(botListingPath());
    },
    "Удалить",
  );
</script>

<Page>
  <Navbar />
  <PageContent>
    <Breadcrumbs>
      <BreadcrumbHome />
      <BreadcrumbDashboard {botInfo} />
    </Breadcrumbs>
    <Heading tag="h3">Управление</Heading>
    <div class="mt-4 flex flex-col gap-3 w-fit">
      <Button color="red" size="xl" outline on:click={stopRunningBot} disabled={botInfo.running_version === null}>
        Остановить бота
      </Button>
      <Button color="red" size="xl" outline on:click={deleteBot}>Удалить бота</Button>
    </div>
  </PageContent>
</Page>
