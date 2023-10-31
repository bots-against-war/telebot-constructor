<script lang="ts">
  import { Text } from "@svelteuidev/core";
  import type { LanguageData } from "../api/types";

  export let languageData: LanguageData;
  export let fullName: boolean = false;
  export let small: boolean = false;
</script>

<Text size={small ? "xs" : "md"}>
  {languageData.emoji || "🌐"}
  {fullName ? languageData.name : languageData.code}
</Text>
