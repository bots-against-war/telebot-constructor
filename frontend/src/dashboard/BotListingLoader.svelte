<script lang="ts">
  import { listBotInfos } from "../api/botInfo";
  import FatalError from "../components/FatalError.svelte";
  import LoadingScreen from "../components/LoadingScreen.svelte";
  import { unwrap } from "../utils.js";
  import BotListing from "./BotListing.svelte";

  const loadBotList = async () => unwrap(await listBotInfos());
</script>

{#await loadBotList()}
  <LoadingScreen />
{:then list}
  <BotListing botInfos={list} />
{:catch error}
  <FatalError {error} />
{/await}
