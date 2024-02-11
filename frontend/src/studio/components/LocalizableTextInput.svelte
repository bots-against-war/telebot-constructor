<script lang="ts">
  import type { ComponentProps } from "svelte";
  import { type LocalizableText } from "../../types";
  import { languageConfigStore } from "../stores";
  import LocalizableTextInputInternal from "./LocalizableTextInputInternal.svelte";

  type $$Props = Omit<ComponentProps<LocalizableTextInputInternal>, "langConfig">;

  export let value: LocalizableText;
</script>

<LocalizableTextInputInternal bind:value langConfig={$languageConfigStore} {...$$restProps} />
