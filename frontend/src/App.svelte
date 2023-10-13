<script lang="ts">
  import { Router, Route, links } from "svelte-routing";
  import { SvelteUIProvider } from "@svelteuidev/core";
  // @ts-expect-error
  import Modal from "svelte-simple-modal";

  import DashboardLoader from "./dashboard/DashboardLoader.svelte";
  import StudioLoader from "./studio/StudioLoader.svelte";
  import Navbar from "./components/Navbar.svelte";
  import GlobalStateProvider from "./GlobalStateProvider.svelte";
</script>

<SvelteUIProvider withNormalizeCSS withGlobalStyles>
  <Modal>
    <div use:links>
      <GlobalStateProvider>
        <Router>
          <Route path="/">
            <Navbar />
            <DashboardLoader />
          </Route>
          <Route path="/studio/:botname" let:params>
            <StudioLoader botName={params.botname} />
          </Route>
          <!-- TODO: separate each route contents to a component -->
          <Route path="/command">
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
          </Route>
        </Router>
      </GlobalStateProvider>
    </div>
  </Modal>
</SvelteUIProvider>
