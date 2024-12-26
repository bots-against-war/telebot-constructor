<script lang="ts">
  import { getBotVersionsPage } from "../../../api/botInfo";
  import FatalError from "../../../components/FatalError.svelte";
  import LoadingScreen from "../../../components/LoadingScreen.svelte";
  import { unwrap } from "../../../utils";
  import Versions from "./Versions.svelte";

  export let botId: string;

  const offset = 0;
  const count = 20;
  const loadFormResultsOrFail = async () => unwrap(await getBotVersionsPage(botId, offset, count));
</script>

{#await loadFormResultsOrFail()}
  <LoadingScreen />
{:then page}
  <Versions {page} />
{:catch error}
  <FatalError {error} />
{/await}
