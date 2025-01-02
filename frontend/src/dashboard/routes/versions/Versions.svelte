<script lang="ts">
  import { t } from "svelte-i18n";
  import { Button, Heading } from "flowbite-svelte";
  import { RocketSolid } from "flowbite-svelte-icons";
  import { getBotVersionsPage } from "../../../api/botInfo";
  import { startBot, stopBot } from "../../../api/lifecycle";
  import type { BotVersionsPage } from "../../../api/types";
  import BotVersionInfoBadge from "../../../components/BotVersionInfoBadge.svelte";
  import BreadcrumbDashboard from "../../../components/breadcrumbs/BreadcrumbDashboard.svelte";
  import BreadcrumbHome from "../../../components/breadcrumbs/BreadcrumbHome.svelte";
  import Breadcrumbs from "../../../components/breadcrumbs/Breadcrumbs.svelte";
  import ConfirmationModal from "../../../components/ConfirmationModal.svelte";
  import Navbar from "../../../components/Navbar.svelte";
  import Page from "../../../components/Page.svelte";
  import PageContent from "../../../components/PageContent.svelte";
  import Pager from "../../../components/Pager.svelte";
  import { studioPath } from "../../../routeUtils";
  import { convert, getModalOpener } from "../../../utils";

  export let page: BotVersionsPage;

  const botInfo = page.bot_info;
  const total = page.total_versions;
  const lastVersion = page.total_versions - 1;

  const open = getModalOpener();
  const publishBot = (verNo: number) => {
    open(ConfirmationModal, {
      text:
        `${$t("dashboard.publish")} v${verNo + 1}` +
        (botInfo.running_version !== null ? ` ${$t("dashboard.instead_of")} v${botInfo.running_version + 1}` : "") +
        "?",
      onConfirm: async () => {
        const resp = await startBot(botInfo.bot_id, { version: verNo });
        if (resp.ok) {
          botInfo.running_version = verNo;
        } else {
          alert(`${$t("dashboard.error_starting_bot")}: ${resp.error}`);
          botInfo.running_version = null;
        }
      },
      confirmButtonLabel: $t("dashboard.publish"),
    });
  };

  const stopPuslishedBot = () => {
    open(ConfirmationModal, {
      text: $t("dashboard.confirm_stop_bot"),
      onConfirm: async () => {
        const resp = await stopBot(botInfo.bot_id);
        if (resp.ok) {
          botInfo.running_version = null;
        } else {
          alert(`${$t("dashboard.error_stopping_bot")}: ${resp.error}`);
        }
      },
      confirmButtonLabel: $t("dashboard.stop_bot"),
    });
  };
</script>

<Page>
  <Navbar />
  <PageContent>
    <Breadcrumbs>
      <BreadcrumbHome />
      <BreadcrumbDashboard {botInfo} />
    </Breadcrumbs>
    <Heading tag="h3">{$t("dashboard.version_history")}</Heading>

    <Pager
      items={page.versions}
      loader={async (offset, count) =>
        convert(await getBotVersionsPage(botInfo.bot_id, offset, count), (page) => page.versions)}
      {total}
      let:items
    >
      <div slot="indices" let:first let:last>
        <strong>{total - last + 1} - {total - first + 1}</strong> / <strong>{total}</strong>
      </div>
      <ol class="relative border-s border-gray-200 mt-2">
        {#each items.toReversed() as ver (ver.version)}
          <li class="mb-2 ms-3 p-2">
            {#if ver.version === botInfo.running_version}
              <div class="absolute w-8 h-8 mt-1 -start-4 text-green-600">
                <RocketSolid class="w-8 h-8" />
              </div>
            {:else}
              <div class="absolute w-3 h-3 bg-gray-300 rounded-full mt-2.5 -start-1.5 border border-white" />
            {/if}
            <div class="flex flex-row gap-4 items-center justify-between">
              <div class="flex-grow">
                <BotVersionInfoBadge {ver} carded={false} />
              </div>
              <div class="flex flex-row gap-1 items-baseline">
                {#if ver.version === botInfo.running_version}
                  <Button size="xs" outline color="red" on:click={stopPuslishedBot}>{$t("dashboard.stop_bot")}</Button>
                {:else}
                  <Button size="xs" outline color="primary" on:click={() => publishBot(ver.version)}>
                    {$t("dashboard.publish")}
                  </Button>
                {/if}
                <Button
                  size="xs"
                  outline
                  href={studioPath(botInfo.bot_id, ver.version === lastVersion ? null : ver.version)}
                >
                  {ver.version === lastVersion ? $t("dashboard.edit") : $t("dashboard.open_readonly")}
                </Button>
              </div>
            </div>
          </li>
        {/each}
      </ol>
    </Pager>
  </PageContent>
</Page>
