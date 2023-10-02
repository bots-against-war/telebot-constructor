<script lang="ts">
  import { listBotConfigs } from "../api/botConfig.js";
  import FatalError from "../components/FatalError.svelte";
  import LoadingScreen from "../components/LoadingScreen.svelte";
  import { unwrap } from "../utils.js";
  import Dashboard from "./Dashboard.svelte";

  const loadBotConfigs = async () => unwrap(await listBotConfigs());
</script>

{#await loadBotConfigs()}
  <LoadingScreen />
{:then botConfigs}
  <Dashboard {botConfigs} />
{:catch error}
  <FatalError {error} />
{/await}
