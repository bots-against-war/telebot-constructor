<script lang="ts">
  import { loadFormResults } from "../../../api/formResults";
  import FatalError from "../../../components/FatalError.svelte";
  import LoadingScreen from "../../../components/LoadingScreen.svelte";
  import { unwrap } from "../../../utils";
  import Form from "./Form.svelte";

  export let botId: string;
  export let formBlockId: string;

  const offset = 0;
  const count = 30;
  const loadFormResultsOrFail = async () => unwrap(await loadFormResults(botId, formBlockId, offset, count));
</script>

{#await loadFormResultsOrFail()}
  <LoadingScreen />
{:then page}
  <Form {page} />
{:catch error}
  <FatalError {error} />
{/await}
