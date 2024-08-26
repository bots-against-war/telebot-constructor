<script lang="ts">
  import { links, Route, Router } from "svelte-routing";
  import { setContext } from "svelte";
  import Modal from "svelte-simple-modal";
  import DashboardLoader from "./dashboard/DashboardLoader.svelte";
  import GlobalStateProvider from "./GlobalStateProvider.svelte";
  import StudioLoader from "./studio/StudioLoader.svelte";
  import FormLoader from "./forms/FormLoader.svelte";

  // Global icon settings for flowbite-icons
  const iconCtx = {
    size: "xs",
    width: 15,
    strokeWidth: "1",
  };
  setContext("iconCtx", iconCtx);
</script>

<GlobalStateProvider>
  <Modal closeButton={false} styleWindow={{ borderRadius: "0" }} closeOnOuterClick={false} closeOnEsc={false}>
    <div use:links>
      <Router>
        <Route path="/">
          <DashboardLoader />
        </Route>
        <Route path="/studio/:botId" let:params>
          <StudioLoader botId={params.botId} />
        </Route>
        <Route path="/forms/:botId/:formBlockId" let:params>
          <FormLoader botId={params.botId} formBlockId={params.formBlockId} />
        </Route>
      </Router>
    </div>
  </Modal>
</GlobalStateProvider>
