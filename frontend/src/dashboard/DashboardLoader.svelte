<script lang="ts">
  import FatalError from "../components/FatalError.svelte";
  import LoadingScreen from "../components/LoadingScreen.svelte";
  import { unwrap } from "../utils.js";
  import Dashboard from "./Dashboard.svelte";
  import { loadBotsInfo } from "../api/botInfo";

  const loadBotInfo = async () => unwrap(await loadBotsInfo());
</script>

{#await loadBotInfo()}
  <LoadingScreen />
{:then botInfos}
  <Dashboard {botInfos} />
{:catch error}
  <FatalError {error} />
{/await}
