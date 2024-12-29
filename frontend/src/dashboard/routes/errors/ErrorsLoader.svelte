<script lang="ts">
  import { loadErrors } from "../../../api/errors";
  import FatalError from "../../../components/FatalError.svelte";
  import LoadingScreen from "../../../components/LoadingScreen.svelte";
  import { unwrap } from "../../../utils";
  import Errors from "./Errors.svelte";

  export let botId: string;

  const DEFAULT_OFFSET = 0;
  const DEFAULT_COUNT = 30;
  const loadOrFail = async () => unwrap(await loadErrors(botId, DEFAULT_OFFSET, DEFAULT_COUNT));
</script>

{#await loadOrFail()}
  <LoadingScreen />
{:then page}
  <Errors {page} />
{:catch error}
  <FatalError {error} />
{/await}
