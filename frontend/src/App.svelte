<script lang="ts">
  import { A } from "flowbite-svelte";
  import { isLoading } from "svelte-i18n";
  import { setContext } from "svelte";
  import { links, Route, Router } from "svelte-routing";
  import Modal from "svelte-simple-modal";
  import GlobalStateProvider from "./GlobalStateProvider.svelte";
  import BotInfoLoader from "./dashboard/BotInfoLoader.svelte";
  import BotListingLoader from "./dashboard/BotListingLoader.svelte";
  import ErrorsLoader from "./dashboard/routes/errors/ErrorsLoader.svelte";
  import FormLoader from "./dashboard/routes/forms/FormLoader.svelte";
  import SettingsLoader from "./dashboard/routes/settings/SettingsLoader.svelte";
  import VersionsLoader from "./dashboard/routes/versions/VersionsLoader.svelte";
  import {
    botListingPath,
    dashboardPath,
    errorsPath,
    formResultsPagePath,
    settingsPath,
    studioPath,
    versionsPagePath,
  } from "./routeUtils";
  import StudioLoader from "./studio/StudioLoader.svelte";
  import { initI18n } from "./i18n";
  import LoadingScreen from "./components/LoadingScreen.svelte";

  initI18n();

  // Global icon settings for flowbite-icons
  const iconCtx = {
    size: "md",
    width: 20,
    strokeWidth: "2",
  };
  setContext("iconCtx", iconCtx);
</script>

{#if $isLoading}
  <LoadingScreen />
{:else}
  <GlobalStateProvider>
    <Modal
      closeButton={false}
      styleWindow={{ borderRadius: "0" }}
      closeOnOuterClick={false}
      closeOnEsc={false}
      styleCloseButton={{ borderRadius: "0" }}
    >
      <div use:links>
        <Router>
          <Route>
            <!-- NOTE: this is a default catch-all route -->
            <BotListingLoader />
          </Route>
          <Route path={dashboardPath(":botId")} let:params>
            <BotInfoLoader botId={params.botId} />
          </Route>
          <Route path={studioPath(":botId", null)} let:params>
            <StudioLoader botId={params.botId} />
          </Route>
          <Route path={versionsPagePath(":botId")} let:params>
            <VersionsLoader botId={params.botId} />
          </Route>
          <Route path={settingsPath(":botId")} let:params>
            <SettingsLoader botId={params.botId} />
          </Route>
          <Route path={formResultsPagePath(":botId", ":formBlockId")} let:params>
            <FormLoader botId={params.botId} formBlockId={params.formBlockId} />
          </Route>
          <Route path={errorsPath(":botId")} let:params>
            <ErrorsLoader botId={params.botId} />
          </Route>
        </Router>
      </div>
    </Modal>
  </GlobalStateProvider>
{/if}
