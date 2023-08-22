<script lang="ts">
  import { listBotConfigs } from "./api/botConfig";
  import type { BotConfig } from "./api/types";
  import { unwrap } from "./utils";

  const BASE_PATH = ""; // TODO: make configurable with Vite build step
  console.log(`Base path = ${BASE_PATH}`);

  let existingConfigs: { [key: string]: BotConfig };

  async function reloadConfigs() {
    existingConfigs = unwrap(await listBotConfigs());
  }

  async function startBot(name: string) {
    const resp = await fetch(BASE_PATH + `/api/start/${name}`, {
      method: "POST",
    });
    const statusEl = document.getElementById(`${name}-status`);
    statusEl.innerHTML = await resp.text();
  }

  async function stopBot(name: string) {
    const resp = await fetch(BASE_PATH + `/api/stop/${name}`, {
      method: "POST",
    });
    const statusEl = document.getElementById(`${name}-status`);
    statusEl.innerHTML = await resp.text();
  }

  async function removeBotConfig(name: string) {
    const resp = await fetch(BASE_PATH + `/api/config/${name}`, {
      method: "DELETE",
    });
    const statusEl = document.getElementById(`${name}-status`);
    statusEl.innerHTML = await resp.text();
    await reloadConfigs();
  }

  async function createNewConfig() {
    const nameEl = document.getElementById("bot_name");
    const tokenSecretNameEl = document.getElementById("bot_token_secret_name");
    const adminChatIdEl = document.getElementById("admin_chat_id");
    const statusEl = document.getElementById("newBotConfigStatus");

    // @ts-ignore
    const name = nameEl.value;
    // @ts-ignore
    const tokenSecretName = tokenSecretNameEl.value;

    const botConfig: BotConfig = {
      token_secret_name: tokenSecretName,
    };

    const admin_chat_id = adminChatIdEl.innerText;
    if (admin_chat_id) {
      if (isNaN(parseInt(admin_chat_id))) {
        statusEl.innerHTML = "Admin chat ID must be a number";
        return;
      } else {
        botConfig.feedback_handler_config = { admin_chat_id: parseInt(admin_chat_id) };
      }
    }

    if (name.length === 0 || tokenSecretName.length === 0) {
      statusEl.innerHTML = `Form not completed. Name and token are required`;
      return;
    }

    console.log(botConfig);
    const resp = await fetch(BASE_PATH + `/api/config/${encodeURIComponent(name)}`, {
      method: "POST",
      body: JSON.stringify(botConfig),
    });
    console.log(resp);

    if (resp.ok) {
      nameEl.innerText = "";
      tokenSecretNameEl.innerText = "";
      adminChatIdEl.innerText = "";
      await reloadConfigs();
    } else {
      statusEl.innerHTML = await resp.text();
    }
  }

  const initReloadConfigPromise = reloadConfigs();
</script>

{#await initReloadConfigPromise}
  Loading...
{:then _}
  <div>
    <h1>Telebot constructor</h1>
    <div>
      <div id="container">
        {#each Object.entries(existingConfigs) as [configName, config], i}
          <h3>{configName}</h3>
          <p>
            Token secret: <code>{config.token_secret_name}</code>
          </p>
          <button on:click={() => startBot(configName)}>Start</button>
          <button on:click={() => stopBot(configName)}>Stop</button>
          <button on:click={() => removeBotConfig(configName)}>Delete</button>
          <div id="{configName}-status" />
        {/each}
      </div>
      <h3>Add bot</h3>
      <form>
        <label for="bot_name">Name</label><br />
        <input type="text" id="bot_name" name="bot_name" /><br />
        <label for="bot_token_secret_name">Token secret name</label><br />
        <input type="text" id="bot_token_secret_name" name="bot_token_secret_name" /><br />
      </form>

      <h3>Feedback Handler</h3>
      <label for="admin_chat_id">Admin chat ID</label><br />
      <input type="text" id="admin_chat_id" name="admin_chat_id" /><br /><br />

      <div class="button">
        <button on:click={createNewConfig}>New bot</button>
        <button on:click={reloadConfigs}>Reload config</button>
      </div>

      <p id="newBotConfigStatus" />
    </div>
  </div>
{/await}

<style>
  h1 {
    transition: color 0.2s;
  }
  button {
    background: var(--color, #fff);
    transform: translate(-2px, -2px);
    filter: drop-shadow(2px 2px 3px rgba(0, 0, 0, 0.2));
    transition: all 0.1s;
  }
  button:hover {
    filter: drop-shadow(0 0 2em #f9ed08);
  }
  p {
    border-top: solid black 1px;
  }
</style>
