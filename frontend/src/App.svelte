<script lang="ts">
  import { setContext } from "svelte";
  import { links, Route, Router } from "svelte-routing";
  import Modal from "svelte-simple-modal";
  import BotInfoLoader from "./dashboard/BotInfoLoader.svelte";
  import BotListingLoader from "./dashboard/BotListingLoader.svelte";
  import FormLoader from "./dashboard/routes/forms/FormLoader.svelte";
  import SettingsLoader from "./dashboard/routes/settings/SettingsLoader.svelte";
  import VersionsLoader from "./dashboard/routes/versions/VersionsLoader.svelte";
  import GlobalStateProvider from "./GlobalStateProvider.svelte";
  import {
    botListingPath,
    dashboardPath,
    formResultsPagePath,
    settingsPath,
    studioPath,
    versionsPagePath,
  } from "./routeUtils";
  import StudioLoader from "./studio/StudioLoader.svelte";

  // Global icon settings for flowbite-icons
  const iconCtx = {
    size: "md",
    width: 20,
    strokeWidth: "2",
  };
  setContext("iconCtx", iconCtx);
</script>

<GlobalStateProvider>
  <Modal closeButton={false} styleWindow={{ borderRadius: "0" }} closeOnOuterClick={false} closeOnEsc={false}>
    <div use:links>
      <Router>
        <Route path={botListingPath()}>
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
      </Router>
    </div>
  </Modal>
</GlobalStateProvider>
