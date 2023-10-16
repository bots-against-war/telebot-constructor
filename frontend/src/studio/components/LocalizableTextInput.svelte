<script lang="ts">
  import LocalizableTextInputInternal from "./LocalizableTextInputInternal.svelte";
  import { type LocalizableText } from "../../types";
  import { languageConfigStore } from "../stores";
  import type { ComponentProps } from "svelte";

  type $$Props = Omit<ComponentProps<LocalizableTextInputInternal>, "languages">;

  export let value: LocalizableText;
</script>

<LocalizableTextInputInternal bind:value langConfig={$languageConfigStore} {...$$restProps} />
