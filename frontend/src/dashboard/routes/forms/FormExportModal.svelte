<script lang="ts">
  import { t } from "svelte-i18n";
  import { A, Button, Heading } from "flowbite-svelte";
  import { apiUrl } from "../../../api/config";
  import type { BotInfo, FormInfo } from "../../../api/types";
  import OptionalDate from "../../../components/inputs/OptionalDate.svelte";

  export let botInfo: BotInfo;
  export let formInfo: FormInfo;

  const path = `/forms/${encodeURIComponent(botInfo.bot_id)}/${encodeURIComponent(formInfo.form_block_id)}/export`;

  const now = Date.now();
  const thirtyDays = 30 * 24 * 60 * 60 * 1000;
  let minDate: Date | null = new Date(now - thirtyDays);
  let maxDate: Date | null = null;

  const toTimestamp = (d: Date) => Math.floor(+d / 1000);

  let exportLink = "";
  $: {
    let queryParts = [];
    if (minDate !== null) {
      queryParts.push(`min_timestamp=${toTimestamp(minDate)}`);
    }
    if (maxDate !== null) {
      queryParts.push(`max_timestamp=${toTimestamp(maxDate)}`);
    }
    const query = queryParts.length > 0 ? "?" + queryParts.join("&") : "";
    exportLink = apiUrl(`${path}${query}`);
  }
</script>

<div class="flex flex-col gap-2">
  <Heading tag="h3">{$t("dashboard.form_results_page.responses_export")}</Heading>
  <div class="text-sm text-gray-600 mt-2">
    {$t("dashboard.form_results_page.csv_format")}
  </div>
  <div class="flex flex-row gap-4">
    <div>
      <Heading tag="h6">{$t("dashboard.form_results_page.starting_from")}</Heading>
      <OptionalDate bind:date={minDate} defaultLabel={$t("dashboard.form_results_page.earliest")} />
    </div>
    <div>
      <Heading tag="h6">{$t("dashboard.form_results_page.up_to")}</Heading>
      <OptionalDate bind:date={maxDate} defaultLabel={$t("dashboard.form_results_page.latest")} />
    </div>
  </div>
  <Button href={exportLink} download="something.csv">{$t("generic.download")}</Button>
</div>
