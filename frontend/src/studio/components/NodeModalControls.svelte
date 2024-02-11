<script lang="ts">
  import { Button } from "flowbite-svelte";
  import { createEventDispatcher } from "svelte";
  import { getModalCloser, sleep } from "../../utils";

  export let saveable: boolean = true;
  export let autoClose: boolean = true;

  const close = getModalCloser();

  const dispatch = createEventDispatcher<{ save: null }>();

  let isSaving = false;
</script>

<div class="flex flex-row gap-2">
  <Button
    disabled={!saveable}
    loading={isSaving}
    on:click={async () => {
      // HACK: after dispatching "save" event, the component may need to do some processing
      // in this case, it's possible that we close modal before the saving is completed
      // then for some reason modal content will not be unmounted after "close" is and
      // subsequently, after opening the modal again there will be multiple copies of its content

      // hopefully, the sleep(...) pause should give "save" event handler enough time to run so that
      // modal content is actually removed from DOM on "close"

      // we can also try fixing this further through patching svelte internals
      // see https://github.com/sveltejs/svelte/issues/6915
      // and https://svelte.dev/repl/1a046c7df84b4145a42df2df4be1cbbb?version=3.48.0
      // or just using synchronous "saveConfig" callback instead of events
      isSaving = true;
      dispatch("save");
      if (autoClose) {
        await sleep(100);
        close();
      } else {
        isSaving = false;
      }
    }}
  >
    Сохранить
  </Button>
  <Button outline on:click={close}>Отмена</Button>
</div>
