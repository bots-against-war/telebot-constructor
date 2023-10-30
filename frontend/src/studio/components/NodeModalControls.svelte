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
        // HACK: after dispatching "save" event, the component may need to do some processing
        // in this case, it's possible we close modal before the saving is actually completed
        // in this case for some reason modal content may not be unmounted after "close" is.
        // subsequently, after opening the modal again there will be multiple copies of its content

        // hopefully, this pause should give "save config" event handler enough time to run so that
        // modal content is actually removed from DOM on "close"

        // in case of bugs we can try fixing this further through patching svelte internals
        // see https://github.com/sveltejs/svelte/issues/6915
        // and https://svelte.dev/repl/1a046c7df84b4145a42df2df4be1cbbb?version=3.48.0
        // or just using synchronous "saveConfig" callback instead of events
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
