<script lang="ts">
  import bawLogo from "../public/baw.svg";
  import { Button } from "@svelteuidev/core";
  import { Router, links } from "svelte-routing";
  import Dashboard from "./dashboard/Dashboard.svelte";
</script>

<Router>
  <div use:links>
    <header id="header" class="header">
      <div class="center" style="flex:0">
        <img src={bawLogo} alt="BAW logo" class="logo" />
      </div>
      <div class="nav-buttons">
        <Button href="/" radius={40} ripple>Управление</Button>
        <Button href="/command" radius={40} ripple>Команда</Button>
        <Button href="/actions" radius={40} ripple>Действия</Button>
        <Button href="/security" radius={40} ripple>Безопасность</Button>
      </div>
    </header>
  </div>
  <Dashboard />
</Router>
