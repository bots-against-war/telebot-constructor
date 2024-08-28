<script lang="ts">
  import {
    A,
    Button,
    Heading,
    Li,
    List,
    P,
    TabItem,
    Table,
    TableBody,
    TableBodyCell,
    TableBodyRow,
    TableHead,
    TableHeadCell,
    Tabs,
  } from "flowbite-svelte";
  import { NODE_TITLE, NodeTypeKey } from "./nodes/display";
  import BlockNameInline from "./components/BlockNameInline.svelte";

  const pClass = "mb-3";
  const headingClass = "mt-10 first:mt-0 mb-4";

  const tdClass = "w-[50%] p-4 align-top";
</script>

<section class="p-4">
  <Heading tag="h3" class={headingClass}>О конструкторе</Heading>
  <P class={pClass}>
    Telebot Constructor позволяет создавать сложные и многоязычные диалоги с различными условиями и решениями на языке
    блок-схем. В этой студии вы собираете логику работы бота из блоков, как конструктор, настраивая его поведение под
    ваши нужды.
  </P>
  <Tabs style="underline" contentClass="p-4 bg-gray-50 pt-6">
    <TabItem open title="Пример">
      <Heading tag="h4" class={headingClass}>Пример бота</Heading>
      <P class={pClass}>
        Представьте, что через ваш бот можно задать вопрос или узнать ваш адрес. Вот как это может выглядеть в работе:
      </P>
      <P class={pClass}>
        <div class="w-full flex flex-col gap-3">
          <strong>Пользователь начинает работу с ботом</strong>
          <div class="bubble right" style="font-family:'Courier New', Courier, monospace; font-weight: bold;">
            /start
          </div>
          <div class="bubble left">
            Привет! Спасибо, что обратились к нам. Чем мы можем помочь?
            <div class="flex flex-row gap-1 w-full mt-2">
              <div class="flex-grow border border-gray-500 w-full text-center py-1">Адрес</div>
              <div class="flex-grow border border-gray-500 w-full text-center py-1">Вопрос</div>
            </div>
          </div>

          <div class="mt-3 border-t border-gray-200 pt-3">Если пользователь выбирает <strong>Адрес</strong></div>
          <div class="bubble left">Проспект Мира, 16</div>

          <div class="mt-3 border-t border-gray-200 pt-3">Если пользователь выбирает <strong>Вопрос</strong></div>
          <div class="bubble left">Напишите ваш вопрос.</div>
          <div class="bubble right">&lt;...&gt;</div>
          <div class="bubble left">Спасибо, мы вам скоро ответим!</div>
          <div>
            Бот пересылает вопрос в ваш рабочий чат, где его видят операторы. Они обрабатывают сообщение и отвечают,
            сообщение передаётся назад пользователю. При необходимости они могут продолжить вести переписку через бот.
          </div>
        </div>
      </P>

      <Heading tag="h4" class={headingClass}>
        <div class="flex flex-row justify-between items-center">
          Как это работает?
          <Button on:click={() => alert("TBD")}>Открыть шаблон</Button>
        </div>
      </Heading>
      <P class={pClass}>
        <Table noborder class="p-0 text-wrap overflow-x-visible">
          <TableHead>
            <TableHeadCell>В Telegram</TableHeadCell>
            <TableHeadCell>В конструкторе</TableHeadCell>
          </TableHead>
          <TableBody tableBodyClass="divide-y">
            <TableBodyRow>
              <TableBodyCell {tdClass}>Пользователь переходит по ссылке на бот и нажимает кнопку "Старт"</TableBodyCell>
              <TableBodyCell {tdClass}>
                Блоки <BlockNameInline key={NodeTypeKey.info} /> и
                <BlockNameInline key={NodeTypeKey.command} /> – это стартовые блоки, обеспечивающие запуск взаимодействия
              </TableBodyCell>
            </TableBodyRow>
            <TableBodyRow>
              <TableBodyCell {tdClass}>
                Пользователь получает приветственное сообщение с двумя кнопками на выбор: "Адрес" и "Вопрос"
              </TableBodyCell>
              <TableBodyCell {tdClass}>
                Блок <BlockNameInline key={NodeTypeKey.menu} /> – здесь задаются варианты выбора и поясняющий текст
              </TableBodyCell>
            </TableBodyRow>
            <TableBodyRow>
              <TableBodyCell {tdClass}>
                Если пользователь выбирает "Адрес", он получает ответ: "Проспект Мира, 16"
              </TableBodyCell>
              <TableBodyCell {tdClass}>
                Блок <BlockNameInline key={NodeTypeKey.content} /> присоединяется к условию "Адрес" и содержит текст ответа
              </TableBodyCell>
            </TableBodyRow>
            <TableBodyRow>
              <TableBodyCell {tdClass}>
                Если пользователь выбирает "Вопрос", он получает сообщение: "Напишите ваш вопрос"
              </TableBodyCell>
              <TableBodyCell {tdClass}>
                Другой блок <BlockNameInline key={NodeTypeKey.content} /> присоединяется к условию "Вопрос" и содержит альтернативный
                текст
              </TableBodyCell>
            </TableBodyRow>
            <TableBodyRow>
              <TableBodyCell {tdClass}>
                Пользователь отправляет сообщение и получает ответ: "Спасибо, мы вам скоро ответим!"
              </TableBodyCell>
              <TableBodyCell {tdClass}>
                Блок <BlockNameInline key={NodeTypeKey.human_operator} /> присоединяется к блоку
                <BlockNameInline key={NodeTypeKey.content} /> и отвечает за связь пользователя с оператор:кой бота. В этом
                блоке выбирается рабочий чат и настраивается автоматический ответ на принятое сообщение
              </TableBodyCell>
            </TableBodyRow>
            <TableBodyRow>
              <TableBodyCell {tdClass}>
                Пользователь получает ваш персональный ответ после обработки сообщения в рабочем чате
              </TableBodyCell>
              <TableBodyCell {tdClass}>
                Ответ из рабочего чата отправляется вручную, и пользователь получает его как обычное сообщение
              </TableBodyCell>
            </TableBodyRow>
          </TableBody>
        </Table>
      </P>
    </TabItem>

    <TabItem title="Понятия">
      <Heading tag="h4" class={headingClass}>О Telegram-ботах</Heading>
      <P class={pClass}>
        Бот в Telegram — это программа, которая работает внутри мессенджера и взаимодействует с пользователями. Проще
        говоря, это автоматизированный собеседник, настроенный на выполнение определённых действий. Боты используют
        <A href="https://core.telegram.org/bots/api">API Telegram</A> для отправки и получения сообщений, управления каналами
        или группами, а также выполнения других функций на платформе. Пользователи общаются с ботом, как с обычным контактом,
        а бот отвечает в зависимости от его настроек и логики.
      </P>

      <Heading tag="h4" class={headingClass}>Что такое API?</Heading>
      <P class={pClass}>
        API (Application Programming Interface) — это набор правил и инструментов, позволяющий программам
        взаимодействовать друг с другом. Представьте API как меню в ресторане: вы выбираете блюдо (функцию или данные),
        а кухня (другая программа) готовит его и подаёт вам. Вы не видите процесс приготовления, но точно знаете, что
        получите в итоге. API работает так же, давая одной программе возможность использовать функции другой программы
        без необходимости погружаться в её внутренние процессы.
      </P>

      <Heading tag="h4" class={headingClass}>Как боты работают в Telegram?</Heading>

      <P class={pClass}>
        Чтобы общаться в Telegram, пользователь создаёт аккаунт, регистрируясь по номеру телефона, и получает доступ
        через пароль и двухфакторную аутентификацию. Телеграм-боты тоже имеют аккаунт, но он создаётся через
        <A href="https://t.me/BotFather">BotFather</A>, а доступ предоставляется через токен. Токен — это уникальный
        ключ, который подтверждает право на использование API и передаётся с каждым запросом к серверу. Как и личный
        пароль, токен должен быть защищён.
      </P>
      <Heading tag="h4" class={headingClass}>Основные ограничения Telegram-ботов:</Heading>

      <P class={pClass}>
        <List>
          <Li>Не могут писать сообщения первыми</Li>
          <Li>Не имеют доступа к истории переписки</Li>
          <Li>Не могут получить номер телефона пользователя без явного запроса</Li>
          <Li>Имеют ограниченный доступ к сообщениям в группах по умолчанию</Li>
          <Li>Не могут загружать и скачивать файлы размером более 20 Мб</Li>
        </List>
      </P>
    </TabItem>

    <TabItem title="Безопасность">TBD</TabItem>
  </Tabs>
</section>

<style>
  .bubble {
    --r: 1.5em; /* the radius */
    --t: 1em; /* the size of the tail */
    max-width: 70%;
    padding: 0.5em 1em;
    border-inline: var(--t) solid #0000;
    border-radius: calc(var(--r) + var(--t)) / var(--r);
    mask:
      radial-gradient(100% 100% at var(--_p) 0, #0000 99%, #000 102%) var(--_p) 100% / var(--t) var(--t) no-repeat,
      linear-gradient(#000 0 0) padding-box;
    background: rgb(229 231 235 / var(--tw-bg-opacity));
    color: black;
  }
  .left {
    --_p: 0;
    border-bottom-left-radius: 0 0;
    place-self: start;
    align-self: flex-start;
  }
  .right {
    --_p: 100%;
    border-bottom-right-radius: 0 0;
    place-self: end;
    align-self: flex-end;
  }
</style>
