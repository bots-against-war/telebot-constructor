<script lang="ts">
  import { Button, Heading, P } from "flowbite-svelte";
  import { getModalCloser } from "../utils";
  import { basicShowcaseTemplate, contentOnlyTemplate, formsTemplate, type Template } from "./templates";

  const close = getModalCloser();

  export let templateSelectedCallback: (arg0: Template) => void;

  const TEMPLATES_DATA = [
    {
      factory: basicShowcaseTemplate,
      title: "Бот из инструкции",
      description: "Простейший бот с одним ветвлением и переходом к живому оператору.",
    },
    {
      factory: contentOnlyTemplate,
      title: "Инфо-бот",
      description: 'Пример использования сложной разметки в блоке "Контент".',
    },
    { factory: formsTemplate, title: "Анкеты приюта", description: "Бот собирает заявки от пользователей." },
    { factory: contentOnlyTemplate, title: "Шаблон 4", description: "Описание шаблона" },
  ];
</script>

<section class="p-4">
  <Heading tag="h3" class="mb-5">Шаблоны</Heading>
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
        }}>Добавить</Button
      >
    </div>
  {/each}
</section>
