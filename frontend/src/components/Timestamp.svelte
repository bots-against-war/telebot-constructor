<script lang="ts">
  import { onDestroy } from "svelte";
  import { date, locale, t, time } from "svelte-i18n";

  export let timestamp: string | number; // ISO string or epoch time in SECONDS (i.e. Python backend format)
  export let timeClass: string = "text-gray-500";
  export let alwaysAbsolute: boolean = false;

  const dt = new Date(
    typeof timestamp === "string"
      ? timestamp
      : // Python returns time in seconds, browser's Date expects milliseconds
        timestamp * 1000,
  );

  let rendered: string;
  let renderedFull: string;

  function renderTimestamp() {
    renderedFull = $date(dt, { format: "long" }) + " " + $time(dt, { format: "medium" });
    const now = new Date();
    const deltaMin = (now.getTime() - dt.getTime()) / (1000 * 60);
    // NOTE: sometimes when we send something to the server and receive a timestamp it can be slightly in the future
    // due to different clocks; so here we allow times up to 10 sec in the future to be "now"
    if (!alwaysAbsolute && -1 / 6 < deltaMin && deltaMin < 60 * 24) {
      if (deltaMin < 1 / 6) {
        rendered = $t("timestamp.now");
        return 5;
      } else if (deltaMin < 1) {
        rendered = `${Math.round(deltaMin * 60)} ${$t("timestamp.sec")}`;
        return 5;
      } else if (deltaMin < 59) {
        rendered = `${Math.round(deltaMin)} ${$t("timestamp.min")}`;
        return 30;
      } else {
        rendered = `${Math.round(deltaMin / 60)} ${$t("timestamp.hrs")}`;
        return null;
      }
    } else {
      if ($locale) {
        const isThisYear = dt.getFullYear() == new Date().getFullYear();
        rendered = dt.toLocaleString(new Intl.Locale($locale), {
          month: "short",
          day: "numeric",
          year: isThisYear ? undefined : "numeric",
          hour: "2-digit",
          minute: "2-digit",
        });
      } else {
        rendered = $date(dt, { format: "medium" }) + " " + $time(dt, { format: "short" });
      }
      return null;
    }
  }

  const rerenderInterval = renderTimestamp();
  if (rerenderInterval !== null) {
    const interval = setInterval(renderTimestamp, 1000 * rerenderInterval);
    onDestroy(() => clearInterval(interval));
  }

  locale.subscribe(() => {
    renderTimestamp();
  });
</script>

<time title={renderedFull} datetime={dt.toISOString()} class={timeClass}>{rendered}</time>
