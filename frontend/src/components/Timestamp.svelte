<script lang="ts">
  import { onDestroy } from "svelte";

  export let timestamp: string | number; // ISO string or epoch time in SECONDS (i.e. Python backend format)
  export let timeClass: string = "";
  export let alwaysAbsolute: boolean = false;

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
    if (!alwaysAbsolute && -1 / 6 < deltaMin && deltaMin < 60 * 24) {
      if (deltaMin < 1 / 6) {
        rendered = "только что";
        return 5;
      } else if (deltaMin < 1) {
        rendered = `${Math.round(deltaMin * 60)} сек`;
        return 5;
      } else if (deltaMin < 59) {
        rendered = `${Math.round(deltaMin)} мин`;
        return 30;
      } else {
        rendered = `${Math.round(deltaMin / 60)} ч`;
        return null;
      }
    } else {
      rendered = dt.toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
      return null;
    }
  }

  const rerenderInterval = renderTimestamp();
  if (rerenderInterval !== null) {
    const interval = setInterval(renderTimestamp, 1000 * rerenderInterval);
    onDestroy(() => clearInterval(interval));
  }
</script>

<time title={dt.toLocaleString()} datetime={dt.toISOString()} class={timeClass}>{rendered}</time>
