<script lang="ts">
  import NavButton from "./NavButton.svelte";
  import bawLogo from "../assets/baw.svg";
</script>

<header>
  <div class="center" style="flex:0">
    <img src={bawLogo} alt="BAW logo" class="logo" />
  </div>
  <div class="nav-buttons">
    <NavButton href="/">Управление</NavButton>
    <NavButton href="/command">Команда</NavButton>
    <NavButton href="/actions">Действия</NavButton>
    <NavButton href="/security">Безопасность</NavButton>
  </div>
</header>

<style>
  header {
    width: 100%;
    height: 88px;
    display: flex;
    flex-flow: row;
    text-align: center;
    align-items: center;
    background: radial-gradient(50.62% 8113.21% at 50.62% 49.54%, #62b1d0 0%, rgba(2, 172, 239, 0.3) 100%);
  }
  .logo {
    height: 5em;
    padding: 1.5em;
    will-change: filter;
    transition: filter 300ms;
  }
  div.nav-buttons {
    display: inline-flex;
    justify-content: center;
    padding: 15px 30px;
    align-items: flex-start;
    gap: 10px;
    margin: auto;
  }
</style>
