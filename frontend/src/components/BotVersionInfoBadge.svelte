<script lang="ts">
  import truncate from "@svackages/truncate";
  import { type BotVersionInfo } from "../api/types";
  import Timestamp from "./Timestamp.svelte";

  export let ver: BotVersionInfo;
</script>

<div class="p-1 border-gray-200 border bg-gray-100">
  <div>
    <strong>v{ver.version}</strong>
    {#if ver.metadata.timestamp}
      · <Timestamp timestamp={ver.metadata.timestamp} timeClass="text-gray-500" />
    {/if}
  </div>
  {#if ver.metadata.message}
    <p use:truncate class="text-gray-600 text-sm max-h-4">{ver.metadata.message}</p>
  {/if}
</div>
