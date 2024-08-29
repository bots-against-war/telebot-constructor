<script lang="ts">
  import { Anchor } from "svelvet";

  export let dummy: boolean = false;
</script>

<div class="anchor-container" class:dummy>
  <Anchor direction="north" multiple={!dummy} input locked={dummy} />
</div>

<style>
  div.anchor-container {
    width: 100%;
    display: flex;
    flex-direction: row;
    justify-content: center;
    position: absolute;
    top: -8px;
    --anchor-width: 16px;
    --anchor-height: 16px;
  }
  div.dummy {
    top: -3px;
    --anchor-width: 6px;
    --anchor-height: 6px;
  }
</style>
