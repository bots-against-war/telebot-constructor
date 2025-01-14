<script lang="ts">
  import { t } from "svelte-i18n";
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
  import { getModalCloser } from "../utils";
  import BlockNameInline from "./components/BlockNameInline.svelte";
  import { NodeTypeKey } from "./nodes/display";

  export let onShowcaseTemplate: () => void;

  const close = getModalCloser();
  const pClass = "mb-3";
  const headingClass = "mt-10 first:mt-0 mb-4";

  const tdClass = "w-[50%] p-4 align-top";
</script>

<section class="p-4">
  <Heading tag="h3" class={headingClass}>{$t("studio.readme.title")}</Heading>
  <P class={pClass}>
    {$t("studio.readme.p1")}
  </P>
  <Tabs style="underline" contentClass="p-4 bg-gray-50 pt-6">
    <TabItem open title={$t("studio.readme.example_bot.tab_title")}>
      <Heading tag="h4" class={headingClass}>{$t("studio.readme.example_bot.h1")}</Heading>
      <P class={pClass}>
        {$t("studio.readme.example_bot.p1")}
      </P>
      <P class={pClass}>
        <div class="w-full flex flex-col gap-3">
          <strong>{$t("studio.readme.example_bot.user_starts")}</strong>
          <div class="bubble right">
            <code>/start</code>
          </div>
          <div class="bubble left">
            {$t("studio.readme.example_bot.bot_response")}
            <div class="flex flex-row gap-1 w-full mt-2">
              <div class="flex-grow border border-gray-500 w-full text-center py-1">
                {$t("studio.readme.example_bot.bot_button_1")}
              </div>
              <div class="flex-grow border border-gray-500 w-full text-center py-1">
                {$t("studio.readme.example_bot.bot_button_2")}
              </div>
            </div>
          </div>

          <div class="mt-3 border-t border-gray-200 pt-3">
            {$t("studio.readme.example_bot.if_user_selects")}
            <strong>{$t("studio.readme.example_bot.bot_button_1")}</strong>
          </div>
          <div class="bubble left">{$t("studio.readme.example_bot.example_address")}</div>

          <div class="mt-3 border-t border-gray-200 pt-3">
            {$t("studio.readme.example_bot.if_user_selects")}
            <strong>{$t("studio.readme.example_bot.bot_button_2")}</strong>
          </div>
          <div class="bubble left">{$t("studio.readme.example_bot.ask_the_question")}</div>
          <div class="bubble right">&lt;...&gt;</div>
          <div class="bubble left">{$t("studio.readme.example_bot.thanks_well_get_back_to_you")}</div>
          <div>
            {$t("studio.readme.example_bot.feedback_handler_descr")}
          </div>
        </div>
      </P>

      <Heading tag="h4" class={headingClass}>
        <div class="flex flex-row justify-between items-center">
          {$t("studio.readme.example_bot.h2")}
          <Button
            on:click={() => {
              onShowcaseTemplate();
              close();
            }}>{$t("studio.readme.example_bot.h2_button")}</Button
          >
        </div>
      </Heading>
      <P class={pClass}>
        <Table noborder class="p-0 text-wrap overflow-x-visible">
          <TableHead>
            <TableHeadCell>{$t("studio.readme.example_bot.in_tg_col")}</TableHeadCell>
            <TableHeadCell>{$t("studio.readme.example_bot.in_constructor_col")}</TableHeadCell>
          </TableHead>
          <TableBody tableBodyClass="divide-y">
            <TableBodyRow>
              <TableBodyCell {tdClass}>{$t("studio.readme.example_bot.user_presses_start")}</TableBodyCell>
              <TableBodyCell {tdClass}>
                <BlockNameInline key={NodeTypeKey.info} />
                {$t("studio.readme.example_bot.and")}
                <BlockNameInline key={NodeTypeKey.command} /> <strong>/start</strong>
                {$t("studio.readme.example_bot.are_start_blocks")}
              </TableBodyCell>
            </TableBodyRow>
            <TableBodyRow>
              <TableBodyCell {tdClass}>
                {$t("studio.readme.example_bot.user_gets_welcome_msg")}
                <strong>{$t("studio.readme.example_bot.bot_button_1")}</strong>
                {$t("studio.readme.example_bot.and")}
                <strong>{$t("studio.readme.example_bot.bot_button_2")}</strong>
              </TableBodyCell>
              <TableBodyCell {tdClass}>
                <BlockNameInline key={NodeTypeKey.menu} />
                {$t("studio.readme.example_bot.is_menu_block")}
              </TableBodyCell>
            </TableBodyRow>
            <TableBodyRow>
              <TableBodyCell {tdClass}>
                {$t("studio.readme.example_bot.is_user_presses_1")}
              </TableBodyCell>
              <TableBodyCell {tdClass}>
                <BlockNameInline key={NodeTypeKey.content} />
                {$t("studio.readme.example_bot.contains_answer_to_1")}
              </TableBodyCell>
            </TableBodyRow>
            <TableBodyRow>
              <TableBodyCell {tdClass}>
                {$t("studio.readme.example_bot.is_user_presses_2")}
              </TableBodyCell>
              <TableBodyCell {tdClass}>
                {$t("studio.readme.example_bot.another_block")}
                <BlockNameInline key={NodeTypeKey.content} />
                {$t("studio.readme.example_bot.contains_answer_to_2")}
              </TableBodyCell>
            </TableBodyRow>
            <TableBodyRow>
              <TableBodyCell {tdClass}>
                {$t("studio.readme.example_bot.is_user_sends_msg")}
              </TableBodyCell>
              <TableBodyCell {tdClass}>
                <BlockNameInline key={NodeTypeKey.human_operator} />
                {$t("studio.readme.example_bot.connects_to_block")}
                <BlockNameInline key={NodeTypeKey.content} />
                {$t("studio.readme.example_bot.and_provides_feedback")}
              </TableBodyCell>
            </TableBodyRow>
            <TableBodyRow>
              <TableBodyCell {tdClass}>
                {$t("studio.readme.example_bot.is_user_gets_response")}
              </TableBodyCell>
              <TableBodyCell {tdClass}>
                {$t("studio.readme.example_bot.answer_is_sent_from_admin_chat")}
              </TableBodyCell>
            </TableBodyRow>
          </TableBody>
        </Table>
      </P>
    </TabItem>

    <TabItem title={$t("studio.readme.glossary.tab_title")}>
      <Heading tag="h4" class={headingClass}>{$t("studio.readme.glossary.h1")}</Heading>
      <P class={pClass}>
        {$t("studio.readme.glossary.p1")}
      </P>

      <Heading tag="h4" class={headingClass}>{$t("studio.readme.glossary.h2")}</Heading>
      <P class={pClass}>
        {$t("studio.readme.glossary.p2")}
      </P>

      <Heading tag="h4" class={headingClass}>{$t("studio.readme.glossary.h3")}</Heading>
      <P class={pClass}>
        {$t("studio.readme.glossary.p3")}
      </P>

      <Heading tag="h4" class={headingClass}>{$t("studio.readme.glossary.h4")}</Heading>
      <P class={pClass}>
        <List>
          <Li>{$t("studio.readme.glossary.p4_l1")}</Li>
          <Li>{$t("studio.readme.glossary.p4_l2")}</Li>
          <Li>{$t("studio.readme.glossary.p4_l3")}</Li>
          <Li>{$t("studio.readme.glossary.p4_l5")}</Li>
          <Li>{$t("studio.readme.glossary.p4_l6")}</Li>
        </List>
      </P>
    </TabItem>

    <TabItem title={$t("studio.readme.blocks.tab_title")}>
      <Heading tag="h4" class={headingClass}>{$t("studio.readme.blocks.h1")}</Heading>
      <Heading tag="h5"><BlockNameInline key={NodeTypeKey.info} /></Heading>
      <P class={pClass}>{$t("studio.readme.blocks.info")}</P>

      <Heading tag="h5"><BlockNameInline key={NodeTypeKey.command} /></Heading>
      <P class={pClass}>
        {$t("studio.readme.blocks.cmd_1")}
      </P>
      <P class={pClass}>
        {@html $t("studio.readme.blocks.cmd_2")}
      </P>

      <Heading tag="h5"><BlockNameInline key={NodeTypeKey.content} /></Heading>
      <P class={pClass}>{$t("studio.readme.blocks.content")}</P>

      <Heading tag="h5"><BlockNameInline key={NodeTypeKey.human_operator} /></Heading>
      <P class={pClass}>
        {$t("studio.readme.blocks.feedback")}
      </P>

      <Heading tag="h5"><BlockNameInline key={NodeTypeKey.language_select} /></Heading>
      <P class={pClass}>
        {$t("studio.readme.blocks.langselect")}
      </P>

      <Heading tag="h5"><BlockNameInline key={NodeTypeKey.menu} /></Heading>
      <P class={pClass}>{$t("studio.readme.blocks.menu")}</P>

      <Heading tag="h5"><BlockNameInline key={NodeTypeKey.form} /></Heading>
      <P class={pClass}>
        {$t("studio.readme.blocks.form")}
      </P>
    </TabItem>
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
