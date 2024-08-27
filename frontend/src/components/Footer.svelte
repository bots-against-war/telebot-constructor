<script>
  import { Footer, FooterLinkGroup } from "flowbite-svelte";
  import { CodeBranchSolid, GithubSolid, MessagesSolid } from "flowbite-svelte-icons";
</script>

<Footer class="border-t-gray-100 border-t-2 py-3 mt-3">
  <FooterLinkGroup
    ulClass="flex flex-wrap gap-x-10 w-full justify-center items-center text-sm text-gray-500 dark:text-gray-400 sm:mt-0"
  >
    <span title="built on __buildTimeReplacedDatetime" class="flex flex-row gap-1 items-center">
      <CodeBranchSolid />
      __buildTimeReplacedVersion</span
    >
    <a
      href="https://github.com/bots-against-war/telebot-constructor"
      target="_blank"
      class="flex flex-row gap-1 items-center"
    >
      <GithubSolid /> Github
    </a>
    <a href="https://t.me/bots_against_war_bot" target="_blank" class="flex flex-row gap-1 items-center">
      <MessagesSolid />
      Связаться с нами
    </a>
  </FooterLinkGroup>
</Footer>
