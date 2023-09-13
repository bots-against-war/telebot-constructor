<script lang="ts">
  import { Button } from "@svelteuidev/core";
  import { getContext } from "svelte";
  import CreateNewBotModal from "./CreateBotModal.svelte";
  // @ts-expect-error
  import type { Context } from "svelte-simple-modal";
  const { open } = getContext<Context>("simple-modal");

  export let selectedBot: string;

  const showNewBotModal = () => open(CreateNewBotModal, { selectedBot: selectedBot });
</script>

<div class="button">
  <p><Button radius={40} on:click={showNewBotModal}>Создать нового бота</Button></p>
</div>

<style>
  .button {
    margin: auto;
  }
</style>
