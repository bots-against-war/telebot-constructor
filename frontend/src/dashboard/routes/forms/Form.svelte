<script lang="ts">
  import truncate from "@svackages/truncate";
  import { Heading, Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell } from "flowbite-svelte";
  import { ChevronLeftOutline, ChevronRightOutline, FloppyDiskOutline } from "flowbite-svelte-icons";
  import { loadFormResults, updateFormTitle } from "../../../api/formResults";
  import type { FormResultsPage } from "../../../api/types";
  import ActionIcon from "../../../components/ActionIcon.svelte";
  import Navbar from "../../../components/Navbar.svelte";
  import Page from "../../../components/Page.svelte";
  import PageContent from "../../../components/PageContent.svelte";
  import Timestamp from "../../../components/Timestamp.svelte";
  import BreadcrumbDashboard from "../../../components/breadcrumbs/BreadcrumbDashboard.svelte";
  import BreadcrumbHome from "../../../components/breadcrumbs/BreadcrumbHome.svelte";
  import Breadcrumbs from "../../../components/breadcrumbs/Breadcrumbs.svelte";
  import EditableText from "../../../components/inputs/EditableText.svelte";
  import { getError, getModalOpener, INFO_MODAL_OPTIONS } from "../../../utils";
  import FormExportModal from "./FormExportModal.svelte";
  import FormResultModal from "./FormResultModal.svelte";

  const open = getModalOpener();

  export let formResultsPage: FormResultsPage;
  export let offset: number;
  export let count: number;

  let botInfo = formResultsPage.bot_info;

  const TIMESTAMP_KEY = "timestamp";
  const USER_KEY = "user";
  let dataHasUsers = formResultsPage.results.some((row) => USER_KEY in row);
  let fieldIds = Object.keys(formResultsPage.info.field_names);

  let editedTitle = formResultsPage.info.title || formResultsPage.info.prompt;

  let formResults = formResultsPage.results;
  let firstIdx: number;
  let lastIdx: number;
  let isStart: boolean;
  let isEnd: boolean;
  $: {
    firstIdx = offset;
    lastIdx = offset + formResults.length - 1;
    isStart = firstIdx === 0;
    isEnd = lastIdx >= formResultsPage.info.total_responses - 1;
  }
  async function loadPage(next: boolean) {
    let sign;
    if (next) {
      if (isEnd) return;
      sign = 1;
    } else {
      if (isStart) return;
      sign = -1;
    }
    const newOffset = offset + sign * count;
    const res = await loadFormResults(botInfo.bot_id, formResultsPage.info.form_block_id, newOffset, count);
    if (res.ok) {
      offset = newOffset;
      formResults = res.data.results;
    } else {
      window.alert("Failed to load page: " + getError(res));
    }
  }

  const iconClass = "w-5 h-5 text-gray-700";
</script>

<Page>
  <Navbar />
  <PageContent>
    <Breadcrumbs>
      <BreadcrumbHome />
      <BreadcrumbDashboard {botInfo} />
    </Breadcrumbs>
    <div class="mb-2 text-left">
      <EditableText
        bind:value={editedTitle}
        on:edited={() => updateFormTitle(botInfo.bot_id, formResultsPage.info.form_block_id, editedTitle)}
      >
        <Heading tag="h3">{editedTitle}</Heading>
      </EditableText>
      <div class="text-md pt-4 flex flex-row gap-5 items-center">
        <span>
          Ответы
          <strong>{firstIdx + 1} - {lastIdx + 1}</strong>
          из
          <strong>{formResultsPage.info.total_responses}</strong>
        </span>
        <div class="flex flex-row gap-2">
          <ActionIcon {iconClass} icon={ChevronLeftOutline} disabled={isStart} on:click={() => loadPage(false)} />
          <ActionIcon {iconClass} icon={ChevronRightOutline} disabled={isEnd} on:click={() => loadPage(true)} />
          <ActionIcon
            {iconClass}
            icon={FloppyDiskOutline}
            on:click={() =>
              open(FormExportModal, { formInfo: formResultsPage.info, botInfo: botInfo }, INFO_MODAL_OPTIONS)}
          />
        </div>
      </div>
    </div>
    <Table hoverable shadow>
      <TableHead>
        <TableHeadCell>Время</TableHeadCell>
        {#if dataHasUsers}
          <TableHeadCell>Пользователь:ница</TableHeadCell>
        {/if}
        {#each fieldIds as fieldId}
          <TableHeadCell>{formResultsPage.info.field_names[fieldId] || fieldId}</TableHeadCell>
        {/each}
      </TableHead>
      <!-- <TableBody tableBodyClass="divide-y"> -->
      <TableBody>
        {#each formResults.toReversed() as res}
          <TableBodyRow
            class="cursor-pointer"
            on:click={() => open(FormResultModal, { result: res, formInfo: formResultsPage.info }, INFO_MODAL_OPTIONS)}
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
  </PageContent>
</Page>
