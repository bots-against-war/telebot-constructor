<script lang="ts">
  import { Button } from "@svelteuidev/core";
  import CreateBotModal from "./CreateBotModal.svelte";
  import { getModalOpener } from "../utils";
  const open = getModalOpener();
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
