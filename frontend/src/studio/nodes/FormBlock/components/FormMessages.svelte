<script lang="ts">
  import { Textarea, Stack } from "@svelteuidev/core";
  import type { FormMessages } from "../../../../api/types";

  export let messages: FormMessages;
</script>

<!-- TODO: hide most field under Advanced and fill with generic default values -->
<Stack>
  <Textarea label="В начале заполнения формы" bind:value={messages.form_start} />
  <Textarea label="Когда поле можно пропустить" bind:value={messages.field_is_skippable} />
  <Textarea label="Когда поле нельзя пропустить" bind:value={messages.field_is_not_skippable} />
  <Textarea label="При некорректном значении" bind:value={messages.please_enter_correct_value} />
  <Textarea label="При неподдерживаемой команде" bind:value={messages.unsupported_command} />
  <Textarea label="При непредвиденной ошибке" bind:value={messages.cancelling_because_of_error} />
</Stack>
