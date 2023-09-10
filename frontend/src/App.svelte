<script lang="ts">
  // @ts-ignore
  import Modal from "svelte-simple-modal";
  import StudioProvider from "./studio/StudioProvider.svelte";
</script>

<Modal>
  <main>
    <div class="constructor">
      <StudioProvider botName="studio-test-bot" />
    </div>
  </main>
</Modal>
