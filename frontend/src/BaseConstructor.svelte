<script lang="ts">
  const BASE_PATH = ""; // TODO: make configurable with Vite build step
  console.log(`Base path = ${BASE_PATH}`);

  let existingConfigs;

  async function reloadConfigs() {
    // const resp = await fetch(BASE_PATH + "/api/config");
    // const existingConfigs = JSON.parse(await resp.text());
    existingConfigs = [
      { name: "bottie", token: "tokeen" },
      { name: "second", token: "sec tok" },
    ];
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
    const tokenEl = document.getElementById("bot_token");
    const adminChatIdEl = document.getElementById("admin_chat_id");

    const name = nameEl.innerText;
    const token = tokenEl.innerText;

    let feedback_handler_config = {};
    const admin_chat_id = adminChatIdEl.innerText;
    if (admin_chat_id) {
      if (isNaN(parseInt(admin_chat_id))) {
        document.getElementById("newBotConfigStatus").innerHTML =
          "Admin chat ID must be a number";
        return;
      } else {
        feedback_handler_config = { admin_chat_id: admin_chat_id };
      }
    }

    if (name.length === 0 || token.length === 0) {
      document.getElementById(
        "newBotConfigStatus"
      ).innerHTML = `Form not completed. Name and token are required`;
      return;
    }

    const token_secret_name = tokenEl.id;
    const respToken = await fetch(
      BASE_PATH + `/api/secrets/${token_secret_name}`,
      { method: "POST", body: tokenEl.innerText }
    );
    if (!respToken.ok) {
      document.getElementById("newBotConfigStatus").innerHTML =
        await respToken.text();
      return;
    }

    const isObjectEmpty = (objectName) => {
      return Object.keys(objectName).length === 0;
    };

    const payload = JSON.stringify({
      token_secret_name: token_secret_name,
      feedback_handler_config: isObjectEmpty(feedback_handler_config)
        ? undefined
        : feedback_handler_config,
    });
    console.log(payload);
    const resp = await fetch(
      BASE_PATH + `/api/config/${encodeURIComponent(name)}`,
      { method: "POST", body: payload }
    );
    console.log(resp);

    if (resp.ok) {
      nameEl.innerText = "";
      tokenEl.innerText = "";
      adminChatIdEl.innerText = "";
      await reloadConfigs();
    } else {
      document.getElementById("newBotConfigStatus").innerHTML =
        await resp.text();
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
        {#each existingConfigs as config, i}
          <h3>{config.name}</h3>
          <p>
            Token: <code>{config.token}</code>
          </p>
          <button on:click={() => startBot(config.name)}>Start</button>
          <button on:click={() => stopBot(config.name)}>Stop</button>
          <button on:click={() => removeBotConfig(config.name)}>Delete</button>
          <div id="{config.name}-status" />
        {/each}
      </div>
      <h3>Add bot</h3>
      <form>
        <label for="bot_name">Name</label><br />
        <input type="text" id="bot_name" name="bot_name" /><br />
        <label for="bot_token">Token</label><br />
        <input type="text" id="bot_token" name="bot_token" /><br />
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
    aspect-ratio: 1;
    border-radius: 50%;
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
