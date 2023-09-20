<script lang="ts">
  import { Button } from "@svelteuidev/core";
  import { getContext } from "svelte";
  import CreateBotModal from "./CreateBotModal.svelte";
  // @ts-expect-error
  import type { Context } from "svelte-simple-modal";

  const { open } = getContext<Context>("simple-modal");
  const showNewBotModal = () => open(CreateBotModal);
</script>

<div class="button">
  <p><Button radius={40} on:click={showNewBotModal}>Создать нового бота</Button></p>
</div>

<style>
  .button {
    margin: auto;
  }
</style>
