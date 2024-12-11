<script lang="ts">
  import { CloseOutline } from "flowbite-svelte-icons";
  import { createEventDispatcher } from "svelte";
  import { mediaUrl } from "../../../api/media";
  import ActionIcon from "../../../components/ActionIcon.svelte";

  export let botId: string;
  export let mediaId: string;

  const href = mediaUrl(mediaId, botId);

  const dispatch = createEventDispatcher<{ delete: string }>();
</script>

<div class="flex justify-center items-center">
  <div class="relative">
    <a {href} target="_blank">
      <img src={href} alt={`attachment with media_id=${mediaId}`} class="object-contain max-w-36 max-h-36" />
    </a>
    <ActionIcon
      icon={CloseOutline}
      buttonClass="absolute w-[15px] h-[15px] right-[-7.5px] top-[-7.5px] !p-0 rounded-full xt-white bg-gray-700 hover:bg-gray-800 border-none"
      iconClass="text-gray-100 w-3 h-3"
      on:click={() => dispatch("delete", mediaId)}
    />
  </div>
</div>
