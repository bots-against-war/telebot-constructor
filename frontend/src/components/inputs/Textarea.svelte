<script lang="ts">
  import { Textarea } from "flowbite-svelte";
  import InputWrapper from "./InputWrapper.svelte";
  import { err } from "../../utils";

  export let value: string;
  export let label: string | null = null;
  export let required: boolean = true;
  export let placeholder: string = "";
  export let description: string | null = null;
  export let error: string | boolean | null = null;
  export let maxLength: number | null = null;
  let name: string = defineName(label);

  function defineName(label: string | null): string {
    // TODO move to utils
    function makeUnique(value: string): string {
      const serializedValue = value.toLocaleLowerCase().replaceAll(" ", "-");
      return addCode(serializedValue);
    }

    function addCode(value: string): string {
      const symbols = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
      let code = "-";
      for (let i = 0; i < 7; ++i) {
        const randomIndex = Math.floor(Math.random() * symbols.length);
        code += symbols.slice(randomIndex, randomIndex + 1);
      }

      return value + code;
    }

    if (label) return makeUnique(label);

    return makeUnique("implicit-input");
  }

  $: localError = maxLength && value.length > maxLength ? `Текст должен быть короче ${maxLength} символов` : null; // TODO move to utils, prevent code repetition
</script>

<InputWrapper {label} {description} error={localError || error} {required}>
  <Textarea {name} rows="2" {placeholder} {required} bind:value />
</InputWrapper>
