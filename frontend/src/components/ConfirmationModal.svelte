<script lang="ts">
  import { Stack, Group, Button, Text } from "@svelteuidev/core";
  import { getModalCloser } from "../utils";

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

<Stack>
  <Text>{text}</Text>
  <Group>
    <Button on:click={closeModal}>Отмена</Button>
    <Button color="red" variant="outline" loading={isConfirming} on:click={confirm}>{confirmButtonLabel}</Button>
  </Group>
</Stack>
