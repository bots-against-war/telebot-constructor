<script lang="ts">
  import truncate from "@svackages/truncate";
  import { Heading } from "flowbite-svelte";
  import { FileCodeOutline } from "flowbite-svelte-icons";
  import { loadErrors as loadBotErrors } from "../../../api/errors";
  import type { BotErrorsPage } from "../../../api/types";
  import ActionIcon from "../../../components/ActionIcon.svelte";
  import Navbar from "../../../components/Navbar.svelte";
  import Page from "../../../components/Page.svelte";
  import PageContent from "../../../components/PageContent.svelte";
  import Pager from "../../../components/Pager.svelte";
  import Timestamp from "../../../components/Timestamp.svelte";
  import BreadcrumbDashboard from "../../../components/breadcrumbs/BreadcrumbDashboard.svelte";
  import BreadcrumbHome from "../../../components/breadcrumbs/BreadcrumbHome.svelte";
  import Breadcrumbs from "../../../components/breadcrumbs/Breadcrumbs.svelte";
  import { convert, getModalOpener, INFO_MODAL_OPTIONS } from "../../../utils";
  import TracebackModal from "./TracebackModal.svelte";

  export let page: BotErrorsPage;

  const open = getModalOpener();
</script>

<Page>
  <Navbar />
  <PageContent>
    <Breadcrumbs>
      <BreadcrumbHome />
      <BreadcrumbDashboard botInfo={page.bot_info} />
    </Breadcrumbs>
    <Heading tag="h3">Ошибки</Heading>
    <Pager
      items={page.errors}
      loader={async (offset, count) =>
        convert(await loadBotErrors(page.bot_info.bot_id, offset, count), (page) => page.errors)}
      let:items
    >
      {#each items.toReversed() as error (error.timestamp)}
        <div class="my-3">
          <div class="flex flex-row gap-3 items-center">
            <Timestamp timestamp={error.timestamp} />
            {#if error.exc_type}
              <strong>{error.exc_type}</strong>
            {/if}
            {#if error.exc_traceback}
              <ActionIcon
                icon={FileCodeOutline}
                on:click={() => open(TracebackModal, { traceback: error.exc_traceback }, INFO_MODAL_OPTIONS)}
              />
            {/if}
          </div>
          <p use:truncate class="max-h-[10vh]">
            {error.message}
          </p>
        </div>
      {/each}
    </Pager>
  </PageContent>
</Page>
