<script lang="ts">
  import { t } from "svelte-i18n";
  import { headerColor, NODE_HUE, NODE_TITLE_KEY, NodeTypeKey } from "../nodes/display";

  export let key: NodeTypeKey;
</script>

<strong class="px-1 py-0.25 rounded-none" style="background-color: {headerColor(NODE_HUE[key])}"
  >{$t(NODE_TITLE_KEY[key])}</strong
>
