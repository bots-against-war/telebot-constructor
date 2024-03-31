<script lang="ts">
  import { onDestroy } from "svelte";

  export let timestamp: string | number; // ISO string or epoch time in SECONDS (i.e. Python backend format)
  export let timeClass: string = "";

  const dt = new Date(
    typeof timestamp === "string"
      ? timestamp
      : // Python returns time in seconds, browser's Date expects milliseconds
        timestamp * 1000,
  );

  let rendered: string;

  function renderTimestamp() {
    const now = new Date();
    const deltaMin = (now.getTime() - dt.getTime()) / (1000 * 60);
    // NOTE: sometimes when we send something to the server and receive a timestamp it can be slightly in the future
    // due to different clocks; so here we allow times up to 10 sec in the future to be "now"
    if (-1 / 6 < deltaMin && deltaMin < 60 * 24) {
      if (deltaMin < 1) {
        rendered = "только что";
      } else if (deltaMin < 59) {
        rendered = `${Math.ceil(deltaMin)}м`;
      } else {
        rendered = `${Math.round(deltaMin / 60)}ч`;
      }
    } else {
      rendered = dt.toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
    }
  }

  renderTimestamp();
  const interval = setInterval(renderTimestamp, 1000 * 20);
  onDestroy(() => clearInterval(interval));
</script>

<time title={dt.toLocaleString()} datetime={dt.toISOString()} class={timeClass}>{rendered}</time>
