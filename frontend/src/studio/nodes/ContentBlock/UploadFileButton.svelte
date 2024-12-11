<script lang="ts">
  import { PlusOutline } from "flowbite-svelte-icons";
  import ActionIcon from "../../../components/ActionIcon.svelte";

  export let disabled: boolean;

  function keydown(ev: KeyboardEvent) {
    if (input === null) return;
    if ([" ", "Enter"].includes(ev.key)) {
      ev.preventDefault();
      input.click();
      input.blur();
    }
  }
  let input: HTMLInputElement | null = null;
</script>

<ActionIcon
  icon={PlusOutline}
  on:keydown={keydown}
  on:click={() => input?.click()}
  iconClass="w-5 h-5 text-gray-700"
  buttonClass="!p-2 bg-none border-none hover:bg-gray-100 w-8 h-8"
  {disabled}
>
  <input bind:this={input} on:change type="file" class="hidden" accept=".png,.jpg,.jpeg" />
</ActionIcon>
