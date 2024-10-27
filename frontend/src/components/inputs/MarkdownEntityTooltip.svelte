<script lang="ts">
  import type { SvelteComponent } from "svelte";
  import type { Newable } from "ts-essentials";
  import ActionIcon from "../ActionIcon.svelte";
  import { makeMarkdownEntity, renderPreview, type MarkdownEntityType } from "./markdown_utils";

  export let icon: Newable<SvelteComponent>;
  export let type: MarkdownEntityType;
  export let name: string;

  const entity = makeMarkdownEntity(name, type, "https://example.com");

  const entityHtml = entity.prefix + entity.processed + entity.suffix;
  const entityRendered = renderPreview(entityHtml);
</script>

<div class="max-w-[400px] flex gap-2 items-center">
  <ActionIcon {icon} title={type} iconClass="w-4 h-4 text-gray-600" size="xs"></ActionIcon>
  <span>{entityHtml}</span>
  <span>→</span>
  <div class="md-preview">{@html entityRendered}</div>
</div>
