<script lang="ts">
  import { getFormResults } from "../api/formResults";
  import FatalError from "../components/FatalError.svelte";
  import LoadingScreen from "../components/LoadingScreen.svelte";
  import { unwrap } from "../utils";
  import Form from "./Form.svelte";

  export let botId: string;
  export let formBlockId: string;

  const loadFormResults = async () => unwrap(await getFormResults(botId, formBlockId, 0, 30));
</script>

{#await loadFormResults()}
  <LoadingScreen />
{:then formResultsPage}
  <Form {botId} {formResultsPage} />
{:catch error}
  <FatalError {error} />
{/await}
