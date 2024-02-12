<script>
  import { Footer, FooterLinkGroup } from "flowbite-svelte";
</script>

<Footer class="border-t-gray-100 border-t-2 py-3 mt-3">
  <FooterLinkGroup
    ulClass="flex flex-wrap gap-x-5 w-full justify-center items-center text-sm text-gray-500 dark:text-gray-400 sm:mt-0"
  >
    <span title="built on __buildTimeReplacedDatetime">__buildTimeReplacedVersion</span>
    <a href="https://github.com/bots-against-war/telebot-constructor" target="_blank">Github</a>
    <a href="https://t.me/bots_against_war_bot" target="_blank">Связаться с нами</a>
  </FooterLinkGroup>
</Footer>
