<script lang="ts">
  import { Input } from "flowbite-svelte";
  import InputWrapper from "./InputWrapper.svelte";
  import { EyeOutline, EyeSlashOutline } from "flowbite-svelte-icons";

  export let value: string;
  export let label: string;
  export let required: boolean = true;
  export let placeholder: string = "";
  export let error: string | boolean | null = null;

  let visible = false;
</script>

<InputWrapper {label} {error}>
  <slot name="description" slot="description" />
  <Input
    {label}
    id={label}
    name={label}
    {required}
    {placeholder}
    type={visible ? "text" : "password"}
    bind:value
    color={error ? "red" : undefined}
  >
    <button slot="right" on:click={() => (visible = !visible)} class="pointer-events-auto">
      {#if visible}
        <EyeOutline class="w-5 h-5" />
      {:else}
        <EyeSlashOutline class="w-5 h-5" />
      {/if}
    </button>
  </Input>
</InputWrapper>
