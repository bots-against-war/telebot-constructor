<script lang="ts">
  import { saveBotConfig } from "../api/botConfig";
  import { Button, TextInput } from "@svelteuidev/core";
  import { getContext } from "svelte";
  import { reloadConfigs } from "./Dashboard.svelte";
  // @ts-expect-error
  import { Context } from "svelte-simple-modal";

  let bot_name = "";
  let newBotConfigStatus = "";
  const { close } = getContext<Context>("simple-modal");
  const closePopup = async () => close();

  async function createNewBot() {
    if (!bot_name) {
      newBotConfigStatus = `Form not completed. Name are required`;
      return;
    }

    const bot_config = {
      token_secret_name: "",
    };
    const resp = await saveBotConfig(bot_name, bot_config);
    console.log(resp);

    if (resp.ok) {
      newBotConfigStatus = "";
      await reloadConfigs();
      await closePopup();
    } else {
      // @ts-expect-error
      newBotConfigStatus = `Failed to save: ${resp.error}`;
    }
  }
</script>

<div>
  <TextInput
    bind:value={bot_name}
    label="Дайте имя боту в конструкторе"
    description="Напишите любое имя (его можно будет поменять): "
    placeholder="Бот волонтер"
  />
  <p><span class="text-status">{newBotConfigStatus || ""}</span></p>
  <div class="save-button">
    <Button radius={20} color="#62B1D0" on:click={createNewBot}>Сохранить</Button>
  </div>
</div>
