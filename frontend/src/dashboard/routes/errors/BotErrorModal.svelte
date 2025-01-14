<script lang="ts">
  import { Heading } from "flowbite-svelte";
  import { t } from "svelte-i18n";
  import type { BotError } from "../../../api/types";
  import Timestamp from "../../../components/Timestamp.svelte";

  export let error: BotError;

  const excDataClass = "block whitespace-pre border-gray-400 border-1 bg-gray-100 p-2 overflow-scroll";
</script>

<div>
  <Timestamp timestamp={error.timestamp} />
  <Heading tag="h5">{$t("generic.error")}</Heading>
  <p class="mt-3">
    <code>
      {error.message}
    </code>
  </p>
  {#if error.exc_data}
    <p class="mt-3">
      <code class={excDataClass}>
        {error.exc_data}
      </code>
    </p>
  {/if}
  {#if error.exc_traceback}
    <p class="mt-3">
      <Heading tag="h6">Traceback</Heading>
      <code class={excDataClass}>
        {error.exc_traceback}
      </code>
    </p>
  {/if}
</div>
