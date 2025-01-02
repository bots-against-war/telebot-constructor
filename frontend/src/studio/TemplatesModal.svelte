<script lang="ts">
  import { t } from "svelte-i18n";
  import { Button, Heading, P } from "flowbite-svelte";
  import { getModalCloser } from "../utils";
  import {
    basicShowcaseTemplate,
    contentOnlyTemplate,
    formsTemplate,
    multilangTemplate,
    festivalBotTemplate,
    type Template,
  } from "./templates";

  const close = getModalCloser();

  export let templateSelectedCallback: (arg0: Template) => void;

  const TEMPLATES_DATA = [
    {
      factory: basicShowcaseTemplate,
      title: $t("studio.templates.tutorial_bot_title"),
      description: $t("studio.templates.tutorial_bot_descr"),
    },
    {
      factory: contentOnlyTemplate,
      title: $t("studio.templates.info_bot_title"),
      description: $t("studio.templates.info_bot_descr"),
    },
    {
      factory: formsTemplate,
      title: $t("studio.templates.forms_bot_title"),
      description: $t("studio.templates.forms_bot_descr"),
    },
    {
      factory: multilangTemplate,
      title: $t("studio.templates.multilang_bot_title"),
      description: $t("studio.templates.multilang_bot_descr"),
    },
    {
      factory: festivalBotTemplate,
      title: $t("studio.templates.menu_bot_title"),
      description: $t("studio.templates.menu_bot_descr"),
    },
  ];
</script>

<section class="p-4">
  <Heading tag="h3" class="mb-5">{$t("studio.templates.title")}</Heading>
  {#each TEMPLATES_DATA as { factory, title, description }}
    <div class="flex flex-row justify-between items-start gap-4 mb-3 pb-3 border-b border-gray-300 last:border-b-0">
      <P class="">
        <Heading tag="h5">{title}</Heading>
        {description}
      </P>
      <Button
        size="sm"
        on:click={() => {
          templateSelectedCallback(factory());
          close();
        }}>{$t("studio.templates.select_template")}</Button
      >
    </div>
  {/each}
</section>
