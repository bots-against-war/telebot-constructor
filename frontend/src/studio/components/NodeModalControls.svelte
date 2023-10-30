<script lang="ts">
  import { createEventDispatcher } from "svelte";

  import { Button, Group } from "@svelteuidev/core";

  import { getModalCloser } from "../../utils";
  import { sleep } from "@svelteuidev/composables";

  export let saveable: boolean = true;

  const close = getModalCloser();

  const dispatch = createEventDispatcher<{ save: null }>();

  let isSaving = false;
</script>

<div style="margin-top: 1em;">
  <Group>
    <Button
      variant="filled"
      disabled={!saveable}
      loading={isSaving}
      on:click={async () => {
        // HACK: in case saving config requires some pre-processing, the content of the modal
        // may not be unmounted after "close" is called on the modal. in this case, after opening
        // the modal again there will be multiple copies of modal content
        // hopefully, this pause should give "save config" callback enough time to complete so that
        // modal content is actually removed from DOM on "close"
        isSaving = true;
        dispatch("save");
        await sleep(100);
        close();
      }}
    >
      Сохранить
    </Button>
    <Button variant="outline" on:click={close}>Отмена</Button>
  </Group>
</div>
