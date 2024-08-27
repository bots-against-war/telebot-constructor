<script lang="ts">
  import { getBotVersionsPage } from "../../../api/botInfo";
  import FatalError from "../../../components/FatalError.svelte";
  import LoadingScreen from "../../../components/LoadingScreen.svelte";
  import { unwrap } from "../../../utils";
  import Versions from "./Versions.svelte";

  export let botId: string;

  // TODO: configurable from query params
  const DEFAULT_OFFSET = 0;
  const DEFAULT_COUNT = 30;
  const loadFormResultsOrFail = async () => unwrap(await getBotVersionsPage(botId, DEFAULT_OFFSET, DEFAULT_COUNT));
</script>

{#await loadFormResultsOrFail()}
  <LoadingScreen />
{:then page}
  <Versions {page} offset={DEFAULT_OFFSET} count={DEFAULT_COUNT} />
{:catch error}
  <FatalError {error} />
{/await}
