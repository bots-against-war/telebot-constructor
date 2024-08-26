<script lang="ts">
  import { Input } from "flowbite-svelte";
  import ActionIcon from "../ActionIcon.svelte";
  import { CheckOutline } from "flowbite-svelte-icons";
  import { createEventDispatcher } from "svelte";

  export let value: string;
  export let placeholder: string | null = null;

  const dispatch = createEventDispatcher<{ startedEditing: null; edited: null }>();

  let isEditing = false;

  function finishEditing() {
    isEditing = false;
    dispatch("edited", null);
  }

  let nameInputEl: HTMLElement | null = null;
</script>

{#if isEditing}
  <div class="flex flex-row gap-3 items-baseline flex-1 me-2">
    <Input class="font-semibold py-1" {placeholder} let:props>
      <input bind:this={nameInputEl} {...props} bind:value on:blur={finishEditing} />
    </Input>
    <ActionIcon icon={CheckOutline} on:click={finishEditing} />
  </div>
{:else}
  <button
    class="font-semibold cursor-text hover:underline p-0 border-none m-0 w-full text-left"
    on:click={() => {
      isEditing = true;
      dispatch("startedEditing", null);
      setTimeout(() => {
        if (nameInputEl) {
          nameInputEl.focus();
        }
      }, 100);
    }}
  >
    <slot />
  </button>
{/if}
