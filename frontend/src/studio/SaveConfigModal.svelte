<script lang="ts">
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
    label="Комментарий"
    description="Будет отображаться в истории версий — опишите, чем эта версия примечательна или что изменилось по сравнению с предыдущей версией"
    placeholder="Добавлена ветка логики, исправлена ошибка в приветственном сообщении, ..."
    required={false}
  />
  <Toggle bind:checked={start}>Опубликовать сразу</Toggle>
  <div class="flex flex-row gap-2">
    <Button
      on:click={() => {
        close();
        callback(versionMessage || null, start);
      }}>Сохранить</Button
    >
    <Button
      color="red"
      outline
      on:click={() => {
        close();
      }}>Отмена</Button
    >
  </div>
</div>
