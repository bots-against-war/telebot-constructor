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
  import { convert, getModalOpener, INFO_MODAL_OPTIONS, truncateText } from "../../../utils";
  import BotErrorModal from "./BotErrorModal.svelte";

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
        <button
          class="block w-full text-left mb-2 pb-2 border-b-gray-300 border-b"
          on:click={() => open(BotErrorModal, { error }, INFO_MODAL_OPTIONS)}
        >
          <div class="flex flex-row gap-3 items-center">
            <Timestamp timestamp={error.timestamp} />
            {#if error.exc_type}
              <strong>{error.exc_type}</strong>
            {/if}
          </div>
          <code>
            {truncateText(error.message, 512)[0]}
          </code>
        </button>
      {/each}
    </Pager>
  </PageContent>
</Page>
