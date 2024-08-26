<script lang="ts">
  import { getBotInfo } from "../api/botInfo";
  import FatalError from "../components/FatalError.svelte";
  import LoadingScreen from "../components/LoadingScreen.svelte";
  import { unwrap } from "../utils.js";
  import BotInfoScreen from "./BotInfo.svelte";

  export let botId: string;

  const loadBotInfo = async () => unwrap(await getBotInfo(botId));
</script>

{#await loadBotInfo()}
  <LoadingScreen />
{:then botInfo}
  <BotInfoScreen {botId} {botInfo} />
{:catch error}
  <FatalError {error} />
{/await}
