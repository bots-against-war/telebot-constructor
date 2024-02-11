<script lang="ts">
  import { listBotInfos } from "../api/botInfo";
  import FatalError from "../components/FatalError.svelte";
  import LoadingScreen from "../components/LoadingScreen.svelte";
  import { unwrap } from "../utils.js";
  import Dashboard from "./Dashboard.svelte";

  const loadBotInfo = async () => unwrap(await listBotInfos());
</script>

{#await loadBotInfo()}
  <LoadingScreen />
{:then botInfos}
  <Dashboard {botInfos} />
{:catch error}
  <FatalError {error} />
{/await}
