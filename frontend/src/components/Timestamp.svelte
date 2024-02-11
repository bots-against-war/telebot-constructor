<script lang="ts">
  import { onDestroy } from "svelte";

  export let isoString: string;

  const dt = new Date(isoString);

  let rendered: string;

  function renderTimestamp() {
    const now = new Date();
    const deltaMin = (now.getTime() - dt.getTime()) / (1000 * 60);
    if (0 < deltaMin && deltaMin < 60 * 24) {
      if (deltaMin < 1) {
        rendered = "только что";
      } else if (deltaMin < 59) {
        rendered = `${Math.ceil(deltaMin)}м`;
      } else {
        rendered = `${Math.round(deltaMin / 60)}ч`;
      }
    } else {
      rendered = dt.toLocaleString();
    }
  }

  renderTimestamp();
  const interval = setInterval(renderTimestamp, 1000 * 60);
  onDestroy(() => clearInterval(interval));
</script>

<span title={dt.toLocaleString()}>{rendered}</span>
