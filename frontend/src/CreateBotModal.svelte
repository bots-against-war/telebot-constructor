<script lang="ts">
  import { listBotConfigs, saveBotConfig } from "./api/botConfig";
  import { unwrap } from "./utils";
  import { Button, TextInput } from "@svelteuidev/core";
  import { getContext } from "svelte";
  // @ts-expect-error
  import { Context } from "svelte-simple-modal";
  import { botConfigs } from "./botConfigsStore";
  const { close } = getContext<Context>("simple-modal");
  const closePopup = async () => close();

  let bot_name = "";

  async function reloadConfigs() {
    const configsFromBackend = unwrap(await listBotConfigs());
    botConfigs.set(configsFromBackend);
  }

  async function createNewBot() {
    const statusEl = document.getElementById("newBotConfigStatus");

    if (!bot_name) {
      statusEl.innerHTML = `Form not completed. Name and token are required`;
      return;
    }

    const bot_config = {
      token_secret_name: "",
    };

    const resp = await saveBotConfig(bot_name, bot_config);
    console.log(resp);

    if (resp.ok) {
      await reloadConfigs();
      await closePopup();
    } else {
      // @ts-expect-error
      statusEl.innerHTML = `Failed to save: ${resp.error}`;
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
  <p id="newBotConfigStatus" style="color: #ffaaaa" />
  <div class="save-button">
    <Button radius={20} color="#62B1D0" on:click={createNewBot}>Сохранить</Button>
  </div>
</div>
