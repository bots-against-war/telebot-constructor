<script lang="ts">
  import { loadFormResults } from "../../../api/formResults";
  import FatalError from "../../../components/FatalError.svelte";
  import LoadingScreen from "../../../components/LoadingScreen.svelte";
  import { unwrap } from "../../../utils";
  import Form from "./Form.svelte";

  export let botId: string;
  export let formBlockId: string;

  // TODO: configurable from query params
  const DEFAULT_OFFSET = 0;
  const DEFAULT_COUNT = 30;
  const loadFormResultsOrFail = async () =>
    unwrap(await loadFormResults(botId, formBlockId, DEFAULT_OFFSET, DEFAULT_COUNT));
</script>

{#await loadFormResultsOrFail()}
  <LoadingScreen />
{:then formResultsPage}
  <Form {formResultsPage} offset={DEFAULT_OFFSET} count={DEFAULT_COUNT} />
{:catch error}
  <FatalError {error} />
{/await}
