<script lang="ts">
  import { getBotInfoShort } from "../../../api/botInfo";
  import FatalError from "../../../components/FatalError.svelte";
  import LoadingScreen from "../../../components/LoadingScreen.svelte";
  import { unwrap } from "../../../utils.js";
  import Settings from "./Settings.svelte";

  export let botId: string;

  const loadBotInfo = async () => unwrap(await getBotInfoShort(botId));
</script>

{#await loadBotInfo()}
  <LoadingScreen />
{:then botInfo}
  <Settings {botInfo} />
{:catch error}
  <FatalError {error} />
{/await}
