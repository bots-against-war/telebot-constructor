<script lang="ts">
  import { t } from "svelte-i18n";
  import { Button, Toggle } from "flowbite-svelte";
  import TextInput from "../components/inputs/TextInput.svelte";
  import { getModalCloser } from "../utils";

  const close = getModalCloser();

  type Callback = (versionMessage: string | null, start: boolean) => any;

  export let callback: Callback;

  let versionMessage = "";
  let start = false;
</script>

<div class="flex flex-col gap-4">
  <TextInput
    bind:value={versionMessage}
    label={$t("studio.save_config.title")}
    description={$t("studio.save_config.description")}
    placeholder={$t("studio.save_config.message_placeholder")}
    required={false}
  />
  <Toggle bind:checked={start}>{$t("studio.save_config.publish_now")}</Toggle>
  <div class="flex flex-row gap-2">
    <Button
      on:click={() => {
        close();
        callback(versionMessage || null, start);
      }}>{$t("generic.save")}</Button
    >
    <Button
      color="red"
      outline
      on:click={() => {
        close();
      }}>{$t("generic.cancel")}</Button
    >
  </div>
</div>
