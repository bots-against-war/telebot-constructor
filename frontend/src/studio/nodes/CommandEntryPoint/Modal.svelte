<script lang="ts">
  import { ButtonGroup, Input, InputAddon } from "flowbite-svelte";
  import type { CommandEntryPoint } from "../../../api/types";
  import SlashIcon from "../../../components/icons/SlashIcon.svelte";
  import InputWrapper from "../../../components/inputs/InputWrapper.svelte";
  import TextInput from "../../../components/inputs/TextInput.svelte";
  import NodeModalBody from "../../components/NodeModalBody.svelte";
  import NodeModalControls from "../../components/NodeModalControls.svelte";
  import { NODE_TITLE } from "../display";
  import InlineCollapsible from "../../../components/InlineCollapsible.svelte";

  export let config: CommandEntryPoint;
  export let onConfigUpdate: (newConfig: CommandEntryPoint) => any;

  function updateConfig() {
    onConfigUpdate({ ...config, command: command, short_description: descr || undefined });
  }

  let command = config.command;
  let descr = config.short_description ?? "";

  let isStartCmd = command === "start"; // non-reactive, on start only
  let commandError: string | undefined;
  $: {
    if (!isStartCmd && command === "start") {
      commandError = "Зарезервированная команда";
    } else if (command.length === 0) {
      commandError = "Команда не может быть пустой";
    } else {
      commandError = undefined;
    }
  }
</script>

<NodeModalBody title={NODE_TITLE.command}>
  <InputWrapper label={null} error={commandError}>
    <ButtonGroup class="w-full" size="sm">
      <InputAddon>
        <SlashIcon size="xl" />
      </InputAddon>
      <Input bind:value={command} disabled={isStartCmd} class="font-mono !text-lg pl-3" />
    </ButtonGroup>
  </InputWrapper>
  <TextInput label="Описание" required={false} bind:value={descr}>
    <details slot="description">
      <summary>
        Для меню рядом с полем ввода сообщения или подсказки при наборе "<code>/</code>".
      </summary>
      В многоязычных ботах это описание не переводится – советуем писать на самом популярном языке или несколько вариантов
      в одну строчку. Например: <code>/help</code> – "помощь" или "помощь/pomoc/assistere".
    </details>
  </TextInput>
  <NodeModalControls saveable={commandError === undefined} on:save={updateConfig} />
</NodeModalBody>
