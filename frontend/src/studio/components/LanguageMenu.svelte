<script lang="ts">
  import { ActionIcon, Menu } from "@svelteuidev/core";
  import { GlobeSolid } from "flowbite-svelte-icons";
  import { languageConfigStore } from "../stores";
  import Language from "../../components/Language.svelte";

  export let selectedLang: string | null = null;
</script>

{#if $languageConfigStore}
  <Menu position="right" placement="center" gutter={15} withArrow zIndex={10000}>
    <ActionIcon slot="control">
      <GlobeSolid />
    </ActionIcon>
    {#each $languageConfigStore.supportedLanguageCodes as language (language)}
      <Menu.Item on:click={() => (selectedLang = language)}>
        <Language {language} tooltip={false} />
      </Menu.Item>
    {/each}
  </Menu>
{/if}
