<script lang="ts">
  import { links, Route, Router } from "svelte-routing";
  // @ts-expect-error
  import Modal from "svelte-simple-modal";

  import DashboardLoader from "./dashboard/DashboardLoader.svelte";
  import StudioLoader from "./studio/StudioLoader.svelte";
  import Navbar from "./components/Navbar.svelte";
  import GlobalStateProvider from "./GlobalStateProvider.svelte";
  import ThemeProvider from "./ThemeProvider.svelte";

  import { setContext } from "svelte";

  // Global icon settings
  const iconCtx = {
    size: "xs",
    width: 15,
    strokeWidth: "1",
  };
  setContext("iconCtx", iconCtx);
</script>

<GlobalStateProvider>
  <ThemeProvider>
    <Modal closeButton={false}>
      <div use:links>
        <Router>
          <Route path="/">
            <Navbar />
            <DashboardLoader />
          </Route>
          <Route path="/studio/:botname" let:params>
            <StudioLoader botName={params.botname} />
          </Route>
          <!-- TODO: separate each route contents to a component -->
          <!-- <Route path="/team">
            <Navbar />
            <p>Команда</p>
          </Route>
          <Route path="/actions">
            <Navbar />
            <p>Действия</p>
          </Route>
          <Route path="/security">
            <Navbar />
            <p>Безопасность</p>
          </Route> -->
        </Router>
      </div>
    </Modal>
  </ThemeProvider>
</GlobalStateProvider>
