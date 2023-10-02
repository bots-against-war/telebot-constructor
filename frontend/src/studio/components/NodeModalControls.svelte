<script lang="ts">
  import { createEventDispatcher } from "svelte";

  import { Button, Group } from "@svelteuidev/core";

  import { getModalCloser } from "../../utils";

  const close = getModalCloser();

  const dispatch = createEventDispatcher();
</script>

<div style="margin-top: 1em;">
  <Group>
    <Button
      variant="filled"
      on:click={() => {
        dispatch("save");
        close();
      }}
    >
      Сохранить
    </Button>
    <Button variant="outline" on:click={close}>Отмена</Button>
  </Group>
</div>
