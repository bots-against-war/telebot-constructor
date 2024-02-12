<script lang="ts">
  import { Navbar, NavBrand, Avatar, Popover, Button } from "flowbite-svelte";
  import logo from "../assets/logo.svg";
  import { loggedInUserStore } from "../globalStateStores";
</script>

<Navbar fluid={true} color="primary">
  <NavBrand href="/">
    <img src={logo} class="h-15" alt="Telebot constructor Logo" />
  </NavBrand>
  <slot>
    <Avatar
      id="avatar-menu"
      src={$loggedInUserStore.userpic !== null ? `data:image/png;base64,${$loggedInUserStore.userpic}` : undefined}
    />
    <Popover trigger="click" class="w-80" triggeredBy="#avatar-menu">
      <div class="flex flex-col gap-4">
        <p>
          {$loggedInUserStore.name}
          <br />
          <span class="font-light text-sm">{$loggedInUserStore.username}</span>
        </p>
        <Button
          color="red"
          outline
          on:click={() => {
            // deleting the cookie by setting it to empty with expire date in the past
            // FIXME: seems like it's not working
            //        maybe create a normal /logout endpoint that will call auth-specific method?
            document.cookie = `tc_access_token=;Expires=${new Date(2000).toUTCString()};Path=/`;
            window.location.reload();
          }}
        >
          Выйти
        </Button>
      </div>
    </Popover>
  </slot>
</Navbar>
