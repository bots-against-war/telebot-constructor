<script lang="ts">
  import { botEventTimestamp, type AnyBotEvent } from "../../api/typeUtils";
  import Timestamp from "../../components/Timestamp.svelte";

  export let events: AnyBotEvent[];
  export let limit: number | null = null;

  if (limit === null) limit = events.length;
</script>

{#if events.length !== 0}
  <ol class="relative border-s border-gray-200 mt-2">
    {#each events
      .toSorted((e1, e2) => botEventTimestamp(e2) - botEventTimestamp(e1))
      .slice(0, limit) as event (event.timestamp)}
      <li class="mb-1 ms-2 p-1">
        <div class="absolute w-2 h-2 bg-gray-300 rounded-full mt-1.5 -start-1 border border-white" />
        <div class="flex flex-row gap-2 items-baseline">
          {#if event.event}
            <span>
              {#if event.event === "started"}
                опубликована {typeof event.version === "number" ? `v${event.version + 1}` : "версия-заглушка"}
              {:else if event.event === "edited"}
                создана v{event.new_version + 1}
              {:else if event.event === "stopped"}
                бот остановлен
              {/if}
            </span>
          {/if}
          {#if event.timestamp}
            · <Timestamp timestamp={event.timestamp} timeClass="text-gray-500" />
          {/if}
        </div>
      </li>
    {/each}
  </ol>
{/if}
