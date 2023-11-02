<script lang="ts">
  import { Header, Group, Image } from "@svelteuidev/core";
  import bawLogo from "../assets/baw.svg";
  import { loggedInUserStore } from "../globalStateStores";
</script>

<Header
  height=""
  override={{
    background: "radial-gradient(50.62% 8113.21% at 50.62% 49.54%, #62b1d0 0%, rgba(2, 172, 239, 0.3) 100%);",
    padding: "10px",
  }}
>
  <Group position="apart">
    <Image src={bawLogo} alt="BAW logo" class="logo" />
    <!-- TODO: navigation will go there -->
    <!-- <div class="nav-buttons">
      <NavButton href="/">Управление</NavButton>
      <NavButton href="/team">Команда</NavButton>
      <NavButton href="/actions">Действия</NavButton>
      <NavButton href="/security">Безопасность</NavButton>
    </div> -->
    {$loggedInUserStore.name}
    <Image
      src={$loggedInUserStore.userpic !== null ? `data:image/png;base64,${$loggedInUserStore.userpic}` : null}
      width={25}
      height={25}
      radius={1000}
      usePlaceholder
    >
      <svelte:fragment slot="placeholder">
        <!-- <QuestionMark /> -->
      </svelte:fragment>
    </Image>
  </Group>
</Header>

<style>
  /* div.nav-buttons {
    display: inline-flex;
    justify-content: center;
    padding: 15px 30px;
    align-items: flex-start;
    gap: 10px;
    margin: auto;
  } */
</style>
