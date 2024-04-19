<script lang="ts">
  import { Avatar } from "flowbite-svelte";
  import { ArrowUpRightFromSquareOutline } from "flowbite-svelte-icons";
  import type { TgBotUser } from "../api/types";
  import ActionIcon from "./ActionIcon.svelte";

  export let botUser: TgBotUser;
</script>

<div class="flex flex-row gap-1 items-start justify-between">
  <div class="flex flex-row gap-1 items-center">
    <Avatar src={botUser.userpic ? `data:image/png;base64,${botUser.userpic}` : undefined} class="w-6 h-6" />
    <span>
      {botUser.name}
      <br />
      <span class="text-gray-500 break-all">
        @{botUser.username}
      </span>
    </span>
  </div>
  <ActionIcon href={`https://t.me/${botUser.username}`} icon={ArrowUpRightFromSquareOutline} />
</div>
