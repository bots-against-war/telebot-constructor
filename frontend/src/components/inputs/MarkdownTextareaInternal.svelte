<!-- HACK: partial copy of internal flowbite's implementation to hack markdown editor into it -->
<script lang="ts">
  import { Toggle, Toolbar, ToolbarGroup } from "flowbite-svelte";
  import {
    BoldSolid,
    ExclamationCircleOutline,
    EyeSlashSolid,
    ItalicSolid,
    LinkSolid,
    QuestionCircleOutline,
    QuoteSolid,
    TextSlashOutline,
  } from "flowbite-svelte-icons";
  import { getContext, SvelteComponent } from "svelte";
  import { twMerge } from "tailwind-merge";
  import type { Newable } from "ts-essentials";
  import ActionIcon from "../ActionIcon.svelte";
  import { makeMarkdownEntity, renderPreview, type MarkdownEntityType } from "./markdown_utils";

  export let value: string;
  export let wrappedClass = "block w-full text-sm border-0 px-0 bg-inherit dark:bg-inherit";
  export let innerWrappedClass = "py-2 px-4 bg-white dark:bg-gray-800";

  const background = getContext("background");
  let wrapperClass;
  $: wrapperClass = twMerge(
    "w-full rounded-lg",
    background ? "bg-white dark:bg-gray-800" : "bg-gray-50 dark:bg-gray-700",
    "text-gray-900 dark:placeholder-gray-400 dark:text-white ",
    "border border-gray-200 dark:border-gray-600",
    $$props.class,
  );
  let textareaClass = wrappedClass;
  const headerClass = (header: boolean) =>
    twMerge(header ? "border-b" : "border-t", "py-2 px-3 border-gray-200 dark:border-gray-600");

  // markdown stuff
  let preview = false;
  let markdownTextarea: HTMLTextAreaElement;

  function addMarkup(type: MarkdownEntityType) {
    if (value === undefined || markdownTextarea === undefined) return;
    let start = markdownTextarea.selectionStart;
    let end = markdownTextarea.selectionEnd;
    let selected = value.slice(start, end);

    let { prefix, suffix, processed } = makeMarkdownEntity(selected, type);
    let before = value.slice(0, start);
    let after = value.slice(end);
    if (type === "blockquote") {
      before = before.trimEnd();
      after = after.trimStart();
    }

    value = before + prefix + processed + suffix + after;
    start = before.length + prefix.length + processed.length;
    end = start;
    // HACK: timeout can be broken / get in into a race condition, think of better solution
    setTimeout(() => {
      markdownTextarea.setSelectionRange(start, end);
      markdownTextarea.focus();
    }, 100);
  }

  const toolbarData: [Newable<SvelteComponent>, MarkdownEntityType][] = [
    [BoldSolid, "bold"],
    [ItalicSolid, "italic"],
    [QuoteSolid, "blockquote"],
    [LinkSolid, "link"],
    [TextSlashOutline, "strikethrough"],
    [EyeSlashSolid, "spoiler"],
  ];
</script>

<div class={wrapperClass}>
  <div class={headerClass(true)}>
    <Toolbar embedded>
      <ToolbarGroup divClass={preview ? "pointer-events-none opacity-40" : ""}>
        {#each toolbarData as [icon, type] (type)}
          <ActionIcon
            {icon}
            title={type}
            iconClass="w-3 h-3 text-gray-600"
            size="xs"
            on:click={() => addMarkup(type)}
          />
        {/each}
        <ActionIcon
          icon={QuestionCircleOutline}
          title="Документация Telegram MarkdownV2"
          iconClass="w-3 h-3 text-gray-600"
          size="xs"
          href="https://github.com/sudoskys/telegramify-markdown?tab=readme-ov-file#use-case"
          target="_blank"
        />
      </ToolbarGroup>
      <ToolbarGroup>
        <Toggle size="small" bind:checked={preview}>
          {#if preview}
            <div class="text-red-600 text-sm flex flex-row items-baseline gap-1">
              <ExclamationCircleOutline />
              <span>Может быть неточным</span>
            </div>
          {:else}
            <span class="text-gray-600 text-sm">Превью</span>
          {/if}
        </Toggle>
      </ToolbarGroup>
    </Toolbar>
  </div>
  <div class={innerWrappedClass}>
    {#if preview}
      <div class="preview">{@html renderPreview(value)}</div>
    {:else}
      <textarea
        bind:value
        on:blur
        on:change
        on:click
        on:contextmenu
        on:focus
        on:input
        on:keydown
        on:keypress
        on:keyup
        on:mouseenter
        on:mouseleave
        on:mouseover
        on:paste
        {...$$restProps}
        class={textareaClass}
        bind:this={markdownTextarea}
      />
    {/if}
  </div>
</div>
