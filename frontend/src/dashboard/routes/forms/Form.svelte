<script lang="ts">
  import truncate from "@svackages/truncate";
  import {
    Button,
    Heading,
    Table,
    TableBody,
    TableBodyCell,
    TableBodyRow,
    TableHead,
    TableHeadCell,
  } from "flowbite-svelte";
  import { FloppyDiskOutline } from "flowbite-svelte-icons";
  import { t } from "svelte-i18n";
  import { loadFormResults, updateFormTitle } from "../../../api/formResults";
  import type { FormResultsPage } from "../../../api/types";
  import Navbar from "../../../components/Navbar.svelte";
  import Page from "../../../components/Page.svelte";
  import PageContent from "../../../components/PageContent.svelte";
  import Pager from "../../../components/Pager.svelte";
  import Timestamp from "../../../components/Timestamp.svelte";
  import BreadcrumbDashboard from "../../../components/breadcrumbs/BreadcrumbDashboard.svelte";
  import BreadcrumbHome from "../../../components/breadcrumbs/BreadcrumbHome.svelte";
  import Breadcrumbs from "../../../components/breadcrumbs/Breadcrumbs.svelte";
  import EditableText from "../../../components/inputs/EditableText.svelte";
  import { convert, getModalOpener, INFO_MODAL_OPTIONS } from "../../../utils";
  import FormExportModal from "./FormExportModal.svelte";
  import FormResultModal from "./FormResultModal.svelte";

  const open = getModalOpener();

  export let page: FormResultsPage;

  let botInfo = page.bot_info;

  const TIMESTAMP_KEY = "timestamp";
  const USER_KEY = "user";
  let dataHasUsers = page.results.some((row) => USER_KEY in row);
  let fieldIds = Object.keys(page.info.field_names);

  let editedTitle = page.info.title || page.info.prompt;
</script>

<Page>
  <Navbar />
  <PageContent>
    <Breadcrumbs>
      <BreadcrumbHome />
      <BreadcrumbDashboard {botInfo} />
    </Breadcrumbs>
    <div class="flex flex-row justify-between">
      <EditableText
        bind:value={editedTitle}
        on:edited={() => updateFormTitle(botInfo.bot_id, page.info.form_block_id, editedTitle)}
      >
        <Heading tag="h3">{editedTitle}</Heading>
      </EditableText>
      <Button
        outline
        on:click={() => open(FormExportModal, { formInfo: page.info, botInfo: botInfo }, INFO_MODAL_OPTIONS)}
      >
        <FloppyDiskOutline class="mr-2" />
        {$t("dashboard.form_results_page.export")}
      </Button>
    </div>
    <Pager
      items={page.results}
      loader={async (offset, count) =>
        convert(await loadFormResults(botInfo.bot_id, page.info.form_block_id, offset, count), (page) => page.results)}
      total={page.info.total_responses}
      let:items
    >
      <span slot="indices" let:first let:last>
        <strong>{first} - {last}</strong> / <strong>{page.info.total_responses}</strong>
      </span>
      <Table hoverable shadow>
        <TableHead>
          <TableHeadCell>{$t("dashboard.form_results_page.timestamp")}</TableHeadCell>
          {#if dataHasUsers}
            <TableHeadCell>{$t("dashboard.form_results_page.user")}</TableHeadCell>
          {/if}
          {#each fieldIds as fieldId}
            <TableHeadCell>{page.info.field_names[fieldId] || fieldId}</TableHeadCell>
          {/each}
        </TableHead>
        <!-- <TableBody tableBodyClass="divide-y"> -->
        <TableBody>
          {#each items.toReversed() as res (res[TIMESTAMP_KEY])}
            <TableBodyRow
              class="cursor-pointer"
              on:click={() => open(FormResultModal, { result: res, formInfo: page.info }, INFO_MODAL_OPTIONS)}
            >
              <TableBodyCell>
                <Timestamp timestamp={res[TIMESTAMP_KEY]} alwaysAbsolute />
              </TableBodyCell>
              {#if dataHasUsers}
                <TableBodyCell>{res[USER_KEY] || ""}</TableBodyCell>
              {/if}
              {#each fieldIds as fieldId}
                <TableBodyCell class="text-wrap max-w-10">
                  <div use:truncate class="max-h-[20vh]">
                    {res[fieldId] || ""}
                  </div>
                </TableBodyCell>
              {/each}
            </TableBodyRow>
          {/each}
        </TableBody>
      </Table>
    </Pager>
  </PageContent>
</Page>
