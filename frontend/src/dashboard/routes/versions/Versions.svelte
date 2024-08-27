<script lang="ts">
  import { Heading } from "flowbite-svelte";
  import type { BotVersionsPage } from "../../../api/types";
  import BotVersionInfoBadge from "../../../components/BotVersionInfoBadge.svelte";
  import BreadcrumbDashboard from "../../../components/breadcrumbs/BreadcrumbDashboard.svelte";
  import BreadcrumbHome from "../../../components/breadcrumbs/BreadcrumbHome.svelte";
  import Breadcrumbs from "../../../components/breadcrumbs/Breadcrumbs.svelte";
  import Navbar from "../../../components/Navbar.svelte";
  import Page from "../../../components/Page.svelte";
  import PageContent from "../../../components/PageContent.svelte";

  export let page: BotVersionsPage;
  export let offset: number;
  export let count: number;
  console.log(page);
</script>

<Page>
  <Navbar />
  <PageContent>
    <Breadcrumbs>
      <BreadcrumbHome />
      <BreadcrumbDashboard botInfo={page.bot_info} />
    </Breadcrumbs>
    <Heading tag="h3">История версий</Heading>
    <ol class="relative border-s border-gray-200 mt-2">
      {#each page.versions.toReversed() as ver (ver.version)}
        <li
          class={"mb-2 ms-2 p-2 rounded-md border-2 " +
            (ver.version === page.bot_info.running_version
              ? "bg-blue-100 border-blue-300 border-2"
              : "border-transparent")}
        >
          <div class="absolute w-3 h-3 bg-gray-300 rounded-full mt-2.5 -start-1.5 border border-white" />
          <div class="flex flex-row gap-4 items-center justify-between">
            <BotVersionInfoBadge {ver} />
            <!-- <div>
              <Button size="xs" disabled={isLoading} outline on:click={() => publishOrStop(ver.version)}>
                {botInfo.running_version === ver.version ? "Остановить" : "Опубликовать"}
              </Button>
              <Button size="xs" outline href={studioPath(botId, ver.version === lastVersion ? null : ver.version)}>
                {lastVersion === ver.version ? "Редактировать" : "Посмотреть"}
              </Button>
            </div> -->
          </div>
        </li>
      {/each}
    </ol>
  </PageContent>
</Page>
