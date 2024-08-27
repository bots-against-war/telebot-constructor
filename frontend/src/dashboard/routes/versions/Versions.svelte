<script lang="ts">
  import type { BotVersionsPage } from "../../../api/types";

  export let page: BotVersionsPage;
  export let offset: number;
  export let count: number;
</script>

<div>
  HELLO WORLD, TOTAL: {page.total_versions}
</div>
