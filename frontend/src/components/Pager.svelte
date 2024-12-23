<script lang="ts" generics="PageItem">
  import { ChevronLeftOutline, ChevronRightOutline } from "flowbite-svelte-icons";
  import type { Result } from "../utils";
  import ActionIcon from "./ActionIcon.svelte";

  export let items: PageItem[];
  export let loader: (offset: number, count: number) => Promise<Result<PageItem[], any>>;
  export let offset = 0;
  export let total: number | null = null;
  export let iconClass = "w-5 h-5 text-gray-700";

  const count = items.length;

  let emptyPageLoaded = false;

  let firstIdx: number;
  let lastIdx: number;
  let isStart: boolean;
  let isEnd: boolean;
  $: {
    firstIdx = offset;
    lastIdx = offset + items.length - 1;
    isStart = firstIdx === 0;
    isEnd = emptyPageLoaded || (total !== null ? lastIdx >= total - 1 : items.length < count);
  }
  async function loadNewPage(next: boolean) {
    let sign;
    if (next) {
      if (isEnd) return;
      sign = 1;
    } else {
      if (isStart) return;
      sign = -1;
    }
    const newOffset = offset + sign * count;
    console.debug(`Loading new offset = ${newOffset} count = ${count}`);
    const res = await loader(newOffset, count);
    if (res.ok) {
      emptyPageLoaded = res.data.length == 0;
      if (!emptyPageLoaded) {
        offset = newOffset;
        items = res.data;
      }
    } else {
      window.alert("Failed to load page: " + res.error);
    }
  }
</script>

<div>
  <div class="flex flex-row gap-2 items-center">
    <div class="text-sm">
      <slot name="indices" first={firstIdx + 1} last={lastIdx + 1} {total}>
        <strong>{firstIdx + 1}</strong> – <strong>{lastIdx + 1}</strong>
        {#if total !== null}
          / <strong>{total}</strong>
        {/if}
      </slot>
    </div>
    <ActionIcon {iconClass} icon={ChevronLeftOutline} disabled={isStart} on:click={() => loadNewPage(false)} />
    <ActionIcon {iconClass} icon={ChevronRightOutline} disabled={isEnd} on:click={() => loadNewPage(true)} />
  </div>
  <slot {items} />
</div>
