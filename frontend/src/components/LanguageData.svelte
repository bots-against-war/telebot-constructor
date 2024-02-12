<script lang="ts">
  import type { LanguageData } from "../api/types";

  export let languageData: LanguageData;
  export let fullName: boolean = false;
</script>

<span>
  {languageData.emoji || "🌐"}
  {fullName ? languageData.name : languageData.code}
</span>
