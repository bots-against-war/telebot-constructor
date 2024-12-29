<!-- Copied from svelte flowbite icons -->
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
  // @ts-expect-error
  export let size = ctx.size || "md";
  // @ts-expect-error
  export let role = ctx.role || "img";
  export let ariaLabel = "slash solid";
</script>

<svg
  xmlns="http://www.w3.org/2000/svg"
  fill="currentColor"
  {...$$restProps}
  class={twMerge(
    "shrink-0",
    // @ts-expect-error
    sizes[size],
    $$props.class,
  )}
  {role}
  aria-label={ariaLabel}
  viewBox="-3 -7 6 35 "
  height="25px"
  on:click
  on:keydown
  on:keyup
  on:focus
  on:blur
  on:mouseenter
  on:mouseleave
  on:mouseover
  on:mouseout
>
  <path
    fill="currentColor"
    d="M 2.946 1.342 L -1.0043 19.9268 a 1 1 -78 0 1 -1.9563 -0.4158 L 0.9897 0.9262 a 1 1 -78 0 1 1.9563 0.4158"
  />
</svg>
