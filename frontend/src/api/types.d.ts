/* eslint-disable */
/**
 * This file was automatically generated by json-schema-to-typescript.
 * DO NOT MODIFY IT BY HAND. Instead, modify the source JSONSchema file,
 * and run json-schema-to-typescript to regenerate this file.
 */

export type DisplayName = string;
export type TokenSecretName = string;
export type EntrypointId = string;
export type Command = string;
export type NextBlockId = string | null;
export type CommandScope = "private" | "group" | "any";
export type ShortDescription = string | null;
export type EntrypointId1 = string;
export type NextBlockId1 = string | null;
export type EntrypointId2 = string;
export type Regex = string;
export type NextBlockId2 = string | null;
export type Entrypoints = UserFlowEntryPointConfig[];
export type BlockId = string;
export type MessageText = string;
export type NextBlockId3 = string | null;
export type BlockId1 = string;
export type CatchAll = boolean;
export type AdminChatId = number;
export type ForumTopicPerUser = boolean;
export type AnonimyzeUsers = boolean;
export type MaxMessagesPerMinute = number;
export type ForwardedToAdminOk = string;
export type Throttling = string;
export type CopiedToUserOk = string;
export type DeletedMessageOk = string;
export type CanNotDeleteMessage = string;
export type HashtagsInAdminChat = boolean;
export type UnansweredHashtag = string | null;
export type HashtagMessageRarerThan = string | null;
export type MessageLogToAdminChat = boolean;
export type BlockId2 = string;
export type Text = string;
export type Label = string;
export type NextBlockId4 = string | null;
export type LinkUrl = string | null;
export type Items = MenuItem[];
export type BackLabel =
  | string
  | {
      [k: string]: string;
    };
export type LockAfterTermination = boolean;
export type IsTextHtml = boolean;
export type BlockId3 = string;
export type FormName = string;
export type Id = string;
export type Propmt = string;
export type IsRequired = boolean;
export type Descr = string;
export type IsMultiline = boolean;
export type ValueFormatter = null;
export type NextField = string | NextFieldMapping | null;
export type IfSkipped = string | null;
export type Default = string;
export type EmptyTextErrorMsg = string;
export type Fields = FormFieldConfig[];
export type FormStart = string;
export type FieldIsSkippable = string;
export type FieldIsNotSkippable = string;
export type PleaseEnterCorrectValue = string;
export type UnsupportedCommand = string;
export type CancellingBecauseOfError = string;
export type FormCompletedNextBlockId = string | null;
export type FormCancelledNextBlockId = string | null;
export type Blocks = UserFlowBlockConfig[];
export type X = number;
export type Y = number;

export interface BotConfig {
  display_name: DisplayName;
  token_secret_name: TokenSecretName;
  user_flow_config: UserFlowConfig | null;
  [k: string]: unknown;
}
export interface UserFlowConfig {
  entrypoints: Entrypoints;
  blocks: Blocks;
  node_display_coords: NodeDisplayCoords;
  [k: string]: unknown;
}
export interface UserFlowEntryPointConfig {
  command: CommandEntryPoint | null;
  catch_all: CatchAllEntryPoint | null;
  regex: RegexMatchEntryPoint | null;
  [k: string]: unknown;
}
/**
 * Basic entrypoint catching Telegram /commands
 */
export interface CommandEntryPoint {
  entrypoint_id: EntrypointId;
  command: Command;
  next_block_id: NextBlockId;
  scope: CommandScope & string;
  short_description: ShortDescription;
  [k: string]: unknown;
}
/**
 * Entrypoint that catches all user messages
 */
export interface CatchAllEntryPoint {
  entrypoint_id: EntrypointId1;
  next_block_id: NextBlockId1;
  [k: string]: unknown;
}
/**
 * Entrypoint matching user messages by searching a regex pattern in text
 */
export interface RegexMatchEntryPoint {
  entrypoint_id: EntrypointId2;
  regex: Regex;
  next_block_id: NextBlockId2;
  [k: string]: unknown;
}
export interface UserFlowBlockConfig {
  message: MessageBlock | null;
  human_operator: HumanOperatorBlock | null;
  menu: MenuBlock | null;
  form: FormBlock | null;
  [k: string]: unknown;
}
/**
 * Simplest user flow block: send message and immediately continue to the next block
 */
export interface MessageBlock {
  block_id: BlockId;
  message_text: MessageText;
  next_block_id: NextBlockId3;
  [k: string]: unknown;
}
/**
 * Terminal block that incapsulates user interaction with a human operator
 */
export interface HumanOperatorBlock {
  block_id: BlockId1;
  catch_all: CatchAll;
  feedback_handler_config: FeedbackHandlerConfig;
  [k: string]: unknown;
}
export interface FeedbackHandlerConfig {
  admin_chat_id: AdminChatId;
  forum_topic_per_user: ForumTopicPerUser;
  anonimyze_users: AnonimyzeUsers;
  max_messages_per_minute: MaxMessagesPerMinute;
  messages_to_user: MessagesToUser;
  messages_to_admin: MessagesToAdmin;
  hashtags_in_admin_chat: HashtagsInAdminChat;
  unanswered_hashtag: UnansweredHashtag;
  hashtag_message_rarer_than: HashtagMessageRarerThan;
  message_log_to_admin_chat: MessageLogToAdminChat;
  [k: string]: unknown;
}
export interface MessagesToUser {
  forwarded_to_admin_ok: ForwardedToAdminOk;
  throttling: Throttling;
  [k: string]: unknown;
}
export interface MessagesToAdmin {
  copied_to_user_ok: CopiedToUserOk;
  deleted_message_ok: DeletedMessageOk;
  can_not_delete_message: CanNotDeleteMessage;
  [k: string]: unknown;
}
/**
 * Multilevel menu block powered by Telegram inline buttons
 */
export interface MenuBlock {
  block_id: BlockId2;
  menu: Menu;
  config: MenuConfig;
  [k: string]: unknown;
}
export interface Menu {
  text: Text;
  items: Items;
  [k: string]: unknown;
}
export interface MenuItem {
  label: Label;
  submenu: Menu | null;
  next_block_id: NextBlockId4;
  link_url: LinkUrl;
  [k: string]: unknown;
}
export interface MenuConfig {
  back_label: BackLabel;
  lock_after_termination: LockAfterTermination;
  is_text_html: IsTextHtml;
  [k: string]: unknown;
}
/**
 * UNFINISHED
 *
 * Block with a series of questions to user with options to export their answers in various formats
 */
export interface FormBlock {
  block_id: BlockId3;
  form_name: FormName;
  fields: Fields;
  messages: FormMessages;
  form_completed_next_block_id: FormCompletedNextBlockId;
  form_cancelled_next_block_id: FormCancelledNextBlockId;
  [k: string]: unknown;
}
export interface FormFieldConfig {
  plain_text: PlainTextFormFieldConfig | null;
  [k: string]: unknown;
}
export interface PlainTextFormFieldConfig {
  id: Id;
  propmt: Propmt;
  is_required: IsRequired;
  result_formatting_opts: FormFieldResultFormattingOpts;
  next_field: NextField;
  empty_text_error_msg: EmptyTextErrorMsg;
  [k: string]: unknown;
}
export interface FormFieldResultFormattingOpts {
  descr: Descr;
  is_multiline: IsMultiline;
  value_formatter: ValueFormatter;
  [k: string]: unknown;
}
export interface NextFieldMapping {
  if_value: IfValue;
  if_skipped: IfSkipped;
  default: Default;
  [k: string]: unknown;
}
export interface IfValue {
  [k: string]: string | null;
}
export interface FormMessages {
  form_start: FormStart;
  field_is_skippable: FieldIsSkippable;
  field_is_not_skippable: FieldIsNotSkippable;
  please_enter_correct_value: PleaseEnterCorrectValue;
  unsupported_command: UnsupportedCommand;
  cancelling_because_of_error: CancellingBecauseOfError;
  [k: string]: unknown;
}
export interface NodeDisplayCoords {
  [k: string]: UserFlowNodePosition;
}
export interface UserFlowNodePosition {
  x: X;
  y: Y;
  [k: string]: unknown;
}
