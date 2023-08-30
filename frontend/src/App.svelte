<script lang="ts">
  import Studio from "./studio/Studio.svelte";

  // @ts-ignore
  import Modal from "svelte-simple-modal";
</script>

<Modal>
  <main>
    <div class="constructor">
      <Studio />
    </div>
  </main>
</Modal>
