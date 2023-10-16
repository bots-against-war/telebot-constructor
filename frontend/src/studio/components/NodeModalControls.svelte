<script lang="ts">
  import { createEventDispatcher } from "svelte";

  import { Button, Group } from "@svelteuidev/core";

  import { getModalCloser } from "../../utils";

  export let saveable: boolean = true;

  const close = getModalCloser();

  const dispatch = createEventDispatcher<{ save: null }>();
</script>

<div style="margin-top: 1em;">
  <Group>
    <Button
      variant="filled"
      disabled={!saveable}
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
