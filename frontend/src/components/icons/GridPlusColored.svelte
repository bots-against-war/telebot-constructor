<script lang="ts">
  import { getContext } from "svelte";
  import { twMerge } from "tailwind-merge";
  const ctx = getContext("iconCtx") ?? {};
  const sizes = {
    xs: "w-3 h-3",
    sm: "w-4 h-4",
    md: "w-5 h-5",
    lg: "w-6 h-6",
    xl: "w-8 h-8",
  };
  export let colors: [string, string, string];
  // @ts-expect-error
  export let size = ctx.size || "md";
  // @ts-expect-error
  export let role = ctx.role || "img";
  // @ts-expect-error
  export let strokeWidth = ctx.strokeWidth || "2";
  // @ts-expect-error
  export let color = ctx.color || "currentColor";
  let ariaDescribedby = "";
  let hasDescription = false;
  export let ariaLabel = "grid plus outline";
</script>

<svg
  xmlns="http://www.w3.org/2000/svg"
  {...$$restProps}
  {color}
  class={twMerge(
    "shrink-0",
    // @ts-expect-error
    sizes[size ?? "md"],
    $$props.class,
  )}
  {role}
  aria-label={ariaLabel}
  aria-describedby={hasDescription ? ariaDescribedby : undefined}
  viewBox="0 0 24 24"
>
  <path
    stroke="currentColor"
    stroke-linecap="round"
    stroke-linejoin="round"
    stroke-width={strokeWidth}
    d="M 14 17 H 20 M 17 20 V 14"
  />
  <path
    stroke="currentColor"
    stroke-linecap="round"
    stroke-linejoin="round"
    stroke-width={strokeWidth}
    fill={colors[0]}
    d="M 4.857 4 H 9.143 C 9.616 4 10 4.384 10 4.857 V 9.143 A 0.857 0.857 0 0 1 9.143 10 H 4.857 A 0.857 0.857 0 0 1 4 9.143 V 4.857 C 4 4.384 4.384 4 4.857 4 Z"
  />
  <path
    stroke="currentColor"
    stroke-linecap="round"
    stroke-linejoin="round"
    stroke-width={strokeWidth}
    fill={colors[1]}
    d="M 14.857 4 H 19.143 C 19.616 4 20 4.384 20 4.857 V 9.143 A 0.857 0.857 0 0 1 19.143 10 H 14.857 A 0.857 0.857 0 0 1 14 9.143 V 4.857 C 14 4.384 14.384 4 14.857 4 Z"
  />
  <path
    stroke="currentColor"
    stroke-linecap="round"
    stroke-linejoin="round"
    stroke-width={strokeWidth}
    fill={colors[2]}
    d="M 4.857 14 H 9.143 C 9.616 14 10 14.384 10 14.857 V 19.143 A 0.857 0.857 0 0 1 9.143 20 H 4.857 A 0.857 0.857 0 0 1 4 19.143 V 14.857 C 4 14.384 4.384 14 4.857 14 Z"
  />
</svg>
