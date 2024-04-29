<script lang="ts">
  import { Button, Heading } from "flowbite-svelte";
  import type { FormResultsPage } from "../api/types";
  import Navbar from "../components/Navbar.svelte";
  import { navigate } from "svelte-routing";
  import { Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell } from "flowbite-svelte";
  import Timestamp from "../components/Timestamp.svelte";

  export let botId: string;
  export let formResultsPage: FormResultsPage;

  const TIMESTAMP_KEY = "timestamp";
  const USER_KEY = "user";
  let dataHasUsers = formResultsPage.results.some((row) => USER_KEY in row);
  let fieldIds = Object.keys(formResultsPage.info.field_names);
</script>

<Navbar>
  <div class="flex gap-2">
    <!-- TODO: bot display name, get from API or from somewhere upper in the hierarchy e.g. via store -->
    <Button outline on:click={() => navigate(`/#${botId}`)}>Назад</Button>
  </div>
</Navbar>
<div class="p-1">
  <Table striped hoverable>
    <caption class="p-5">
      <Heading tag="h3">{formResultsPage.info.prompt}</Heading>
    </caption>
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
      {#each formResultsPage.results as res}
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
</div>
