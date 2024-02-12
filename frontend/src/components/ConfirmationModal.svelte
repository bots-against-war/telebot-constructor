<script lang="ts">
  import { Button } from "flowbite-svelte";
  import { getModalCloser } from "../utils";
  import ButtonLoadingSpinner from "./ButtonLoadingSpinner.svelte";

  const closeModal = getModalCloser();

  export let text: string;
  export let onConfirm: () => Promise<any>;
  export let confirmButtonLabel: string;

  let isConfirming = false;
  async function confirm() {
    isConfirming = true;
    await onConfirm();
    isConfirming = false;
    closeModal();
  }
</script>

<div class="flex flex-col gap-4">
  <p>{text}</p>
  <div>
    <Button on:click={closeModal}>Отмена</Button>
    <Button color="red" outline on:click={confirm}>
      <ButtonLoadingSpinner loading={isConfirming} />
      {confirmButtonLabel}
    </Button>
  </div>
</div>
