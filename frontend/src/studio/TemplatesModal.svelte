<script lang="ts">
  import { Button, Heading, P } from "flowbite-svelte";
  import { contentOnlyTemplate, type Template } from "./templates";
  import { getModalCloser } from "../utils";

  const close = getModalCloser();

  export let templateSelectedCallback: (arg0: Template) => void;
</script>

<section class="p-4">
  <Heading tag="h3">Шаблоны</Heading>
  <P>
    <Button
      on:click={() => {
        templateSelectedCallback(contentOnlyTemplate());
        close();
      }}>Добавить</Button
    >
  </P>
</section>
