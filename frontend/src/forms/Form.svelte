<script lang="ts">
  import { Heading, Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell } from "flowbite-svelte";
  import { ChevronLeftOutline, ChevronRightOutline } from "flowbite-svelte-icons";
  import { loadFormResults, updateFormTitle } from "../api/formResults";
  import type { FormResultsPage } from "../api/types";
  import ActionIcon from "../components/ActionIcon.svelte";
  import Navbar from "../components/Navbar.svelte";
  import Page from "../components/Page.svelte";
  import PageContent from "../components/PageContent.svelte";
  import Timestamp from "../components/Timestamp.svelte";
  import BreadcrumbDashboard from "../components/breadcrumbs/BreadcrumbDashboard.svelte";
  import BreadcrumbHome from "../components/breadcrumbs/BreadcrumbHome.svelte";
  import Breadcrumbs from "../components/breadcrumbs/Breadcrumbs.svelte";
  import EditableText from "../components/inputs/EditableText.svelte";
  import { getError } from "../utils";

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
</script>

<Page>
  <Navbar />
  <PageContent>
    <Breadcrumbs>
      <BreadcrumbHome />
      <BreadcrumbDashboard {botInfo} />
    </Breadcrumbs>
    <div class="my-2 text-left">
      <EditableText
        bind:value={editedTitle}
        on:edited={() => updateFormTitle(botInfo.bot_id, formResultsPage.info.form_block_id, editedTitle)}
      >
        <Heading tag="h3">{editedTitle}</Heading>
      </EditableText>
      <div class="text-lg pt-4 flex flex-row gap-5">
        <span>
          Ответы
          <strong>{firstIdx + 1} - {lastIdx + 1}</strong>
          из
          <strong>{formResultsPage.info.total_responses}</strong>
        </span>
        <div>
          <ActionIcon icon={ChevronLeftOutline} disabled={isStart} on:click={() => loadPage(false)} />
          <ActionIcon icon={ChevronRightOutline} disabled={isEnd} on:click={() => loadPage(true)} />
        </div>
      </div>
      <span class="text-gray-400">TBD: скачать результаты в CSV, фильтрация, сортировка, ...</span>
    </div>
    <Table hoverable shadow>
      <TableHead>
        <TableHeadCell>Время</TableHeadCell>
        {#if dataHasUsers}
          <TableHeadCell>Юзер:ка</TableHeadCell>
        {/if}
        {#each fieldIds as fieldId}
          <TableHeadCell>{formResultsPage.info.field_names[fieldId] || fieldId}</TableHeadCell>
        {/each}
      </TableHead>
      <!-- <TableBody tableBodyClass="divide-y"> -->
      <TableBody>
        {#each formResults.toReversed() as res}
          <TableBodyRow>
            <TableBodyCell>
              <Timestamp timestamp={res[TIMESTAMP_KEY]} alwaysAbsolute />
            </TableBodyCell>
            {#if dataHasUsers}
              <TableBodyCell>{res[USER_KEY] || ""}</TableBodyCell>
            {/if}
            {#each fieldIds as fieldId}
              <TableBodyCell>{res[fieldId] || ""}</TableBodyCell>
            {/each}
          </TableBodyRow>
        {/each}
      </TableBody>
    </Table>
  </PageContent>
</Page>
