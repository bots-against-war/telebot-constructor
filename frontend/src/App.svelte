<script lang="ts">
  import bawLogo from "../public/baw.svg";
  import { Button } from "@svelteuidev/core";
  import Constructor from "./CreateBotButton.svelte";
  // @ts-expect-error
  import Modal from "svelte-simple-modal";
  import { Route, Router, links } from "svelte-routing";
  import ArrayBots from "./components/ArrayBots.svelte";
</script>

<div use:links>
  <Router>
    <header id="header" class="header">
      <div class="center" style="flex:0">
        <img src={bawLogo} alt="BAW logo" class="logo" />
      </div>
      <div class="nav-buttons waves-effect waves-light">
        <Button href="/" radius={40} ripple>Управление</Button>
        <Button href="/command" radius={40} ripple>Команда</Button>
        <Button href="/actions" radius={40} ripple>Действия</Button>
        <Button href="/security" radius={40} ripple>Безопасность</Button>
      </div>
    </header>
  </Router>
</div>

<Router>
  <Route path="/">
    <div style="display:flex; flex-flow: column; height:100%;">
      <div class="center, text">
        <p>
          Добро пожаловать в B.A.W., современный конструктор чат-ботов, который поможет вашей инициативе стать еще ближе
          к пользователям.
        </p>
      </div>
      <div class="center">
        <Modal><Constructor /></Modal>
      </div>
      <div class="center">
        <ArrayBots />
      </div>
    </div>
  </Route>
  <Route path="/command">
    <div class="center, text">
      <p>Команда</p>
    </div>
  </Route>
  <Route path="/actions">
    <div class="center, text">
      <p>Действия</p>
    </div>
  </Route>
  <Route path="/security">
    <div class="center, text">
      <p>Безопасность</p>
    </div>
  </Route>
</Router>

<style>
  .center {
    text-align: center;
    display: flex;
    flex-flow: column;
    justify-content: center;
  }

  .nav-buttons {
    display: inline-flex;
    justify-content: center;
    padding: 15px 30px;
    align-items: flex-start;
    gap: 10px;
    margin: auto;
  }

  .header {
    width: 100%;
    height: 88px;

    display: flex;
    flex-flow: row;

    text-align: center;
    align-items: center;

    background: radial-gradient(8113.21% 50.62% at 50.62% 49.54%, #62b1d0 0%, rgba(2, 172, 239, 0.3) 100%);
  }

  .logo {
    height: 5em;
    padding: 1.5em;
    will-change: filter;
    transition: filter 300ms;
  }

  .text {
    flex-shrink: 0;

    color: var(--text, #1c1c1c);
    text-align: center;
    font-family: Roboto,ui-monospace;
    font-size: 32px;
    font-style: normal;
    font-weight: 400;
    line-height: normal;
  }
</style>
