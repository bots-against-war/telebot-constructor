<script lang="ts">
  import { Dropdown, DropdownItem } from "flowbite-svelte";
  import ActionIcon from "../../components/ActionIcon.svelte";

  import { GlobeSolid } from "flowbite-svelte-icons";
  import Language from "../../components/Language.svelte";
  import { languageConfigStore } from "../stores";

  export let selectedLang: string | null = null;

  let dropdownOpen = false;
  const langMenuId = `openLanguageMenu-${crypto.randomUUID()}`;
</script>

{#if $languageConfigStore}
  <div id={langMenuId}>
    <ActionIcon icon={GlobeSolid} />
  </div>
  <Dropdown bind:open={dropdownOpen} triggeredBy="#{langMenuId}" placement="right">
    {#each $languageConfigStore.supportedLanguageCodes as language (language)}
      <DropdownItem
        class="text-nowrap p-2"
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
