<script lang="ts">
  // import { ActionIcon, Menu } from "@svelteuidev/core";
  import ActionIcon from "../../components/ActionIcon.svelte";
  import { Dropdown, DropdownItem, DropdownDivider, DropdownHeader } from "flowbite-svelte";

  import { GlobeSolid } from "flowbite-svelte-icons";
  import Language from "../../components/Language.svelte";
  import { languageConfigStore } from "../stores";

  export let selectedLang: string | null = null;

  let dropdownOpen = false;
  const langMenuId = crypto.randomUUID();
</script>

{#if $languageConfigStore}
  <div id="openLanguageMenu-{langMenuId}">
    <ActionIcon icon={GlobeSolid} />
  </div>
  <Dropdown bind:open={dropdownOpen} triggeredBy="#openLanguageMenu-{langMenuId}" placement="right">
    {#each $languageConfigStore.supportedLanguageCodes as language (language)}
      <DropdownItem
        on:click={() => {
          selectedLang = language;
          dropdownOpen = false;
        }}
      >
        <Language {language} tooltip={false} />
      </DropdownItem>
    {/each}
  </Dropdown>
{/if}
