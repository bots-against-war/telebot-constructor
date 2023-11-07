<script lang="ts">
  import { Header, Group, Image, Menu, Text, Anchor, Stack } from "@svelteuidev/core";
  import logo from "../assets/logo.svg";
  import { loggedInUserStore } from "../globalStateStores";
  import { QuestionCircleOutline } from "flowbite-svelte-icons";
</script>

<Header
  height=""
  override={{
    background: "radial-gradient(50.62% 8113.21% at 50.62% 49.54%, #62b1d0 0%, rgba(2, 172, 239, 0.3) 100%);",
    padding: "5px",
  }}
>
  <Group position="apart" noWrap>
    <Image src={logo} alt="Telebot constructor logo" height={40} />
    <!-- TODO: navigation will go there -->
    <!-- <div class="nav-buttons">
      <NavButton href="/">Управление</NavButton>
      <NavButton href="/team">Команда</NavButton>
      <NavButton href="/actions">Действия</NavButton>
      <NavButton href="/security">Безопасность</NavButton>
    </div> -->
    <slot>
      <Menu>
        <Image
          slot="control"
          src={$loggedInUserStore.userpic !== null ? `data:image/png;base64,${$loggedInUserStore.userpic}` : null}
          width={30}
          height={30}
          radius={1000}
          usePlaceholder
          override={{ cursor: "pointer" }}
        >
          <svelte:fragment slot="placeholder">
            <QuestionCircleOutline />
          </svelte:fragment>
        </Image>
        <Stack>
          <Text>
            {$loggedInUserStore.name}
            <br />
            <Text color="dimmed">
              {$loggedInUserStore.username}
            </Text>
          </Text>
          <Anchor
            on:click={() => {
              // deleting the cookie by setting it to empty with expire date in the past
              // FIXME: seems like it's not working
              //        maybe create a normal /logout endpoint that will call auth-specific method?
              document.cookie = `tc_access_token=;Expires=${new Date(2000).toUTCString()};Path=/`;
              window.location.reload();
            }}>Выйти</Anchor
          >
        </Stack>
      </Menu>
    </slot>
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
