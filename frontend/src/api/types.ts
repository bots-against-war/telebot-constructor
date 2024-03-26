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
export type Text =
  | string
  | {
      [k: string]: string;
    };
export type ContentTextMarkup = "none" | "html" | "markdown";
export type Image = string | null;
export type Attachments = ContentBlockContentAttachment[];
export type Contents = Content[];
export type NextBlockId3 = string | null;
export type BlockId1 = string;
export type CatchAll = boolean;
export type AdminChatId = number;
export type ForumTopicPerUser = boolean;
export type AnonimyzeUsers = boolean;
export type MaxMessagesPerMinute = number;
export type ForwardedToAdminOk =
  | string
  | {
      [k: string]: string;
    };
export type Throttling =
  | string
  | {
      [k: string]: string;
    };
export type CopiedToUserOk = string;
export type DeletedMessageOk = string;
export type CanNotDeleteMessage = string;
export type HashtagsInAdminChat = boolean;
export type UnansweredHashtag = string | null;
export type HashtagMessageRarerThan = string | null;
export type MessageLogToAdminChat = boolean;
export type BlockId2 = string;
export type Text1 =
  | string
  | {
      [k: string]: string;
    };
export type Label =
  | string
  | {
      [k: string]: string;
    };
export type NextBlockId4 = string | null;
export type LinkUrl = string | null;
export type Items = MenuItem[];
export type MenuMechanism = "inline_buttons" | "reply_keyboard";
export type BackLabel =
  | string
  | {
      [k: string]: string;
    }
  | null;
export type LockAfterTermination = boolean;
export type BlockId3 = string;
export type FormName = string;
export type Id = string;
export type Name = string;
export type Prompt =
  | string
  | {
      [k: string]: string;
    };
export type IsRequired = boolean;
export type ResultFormatting = FormFieldResultFormattingOpts | "auto" | null;
export type Descr =
  | string
  | {
      [k: string]: string;
    };
export type IsMultiline = boolean;
export type ValueFormatter = null;
export type IsLongText = boolean;
export type EmptyTextErrorMsg =
  | string
  | {
      [k: string]: string;
    };
export type Id1 = string;
export type Name1 = string;
export type Prompt1 =
  | string
  | {
      [k: string]: string;
    };
export type IsRequired1 = boolean;
export type ResultFormatting1 = FormFieldResultFormattingOpts | "auto" | null;
export type Id2 = string;
export type Label1 =
  | string
  | {
      [k: string]: string;
    };
export type Options = EnumOption[];
export type InvalidEnumErrorMsg =
  | string
  | {
      [k: string]: string;
    };
export type Members1 = BranchingFormMemberConfig[];
export type ConditionMatchValue = string | null;
export type Members = BranchingFormMemberConfig[];
export type FormStart =
  | string
  | {
      [k: string]: string;
    };
export type CancelCommandIs =
  | string
  | {
      [k: string]: string;
    };
export type FieldIsSkippable =
  | string
  | {
      [k: string]: string;
    };
export type FieldIsNotSkippable =
  | string
  | {
      [k: string]: string;
    };
export type PleaseEnterCorrectValue =
  | string
  | {
      [k: string]: string;
    };
export type UnsupportedCommand =
  | string
  | {
      [k: string]: string;
    };
export type EchoToUser = boolean;
export type IsAnonymous = boolean;
export type ChatId = string | number;
export type ViaFeedbackHandler = boolean;
export type FormCompletedNextBlockId = string | null;
export type FormCancelledNextBlockId = string | null;
export type BlockId4 = string;
export type IsBlocking = boolean;
export type EmojiButtons = boolean;
export type SupportedLanguages = string[];
export type LanguageSelectedNextBlockId = string | null;
export type NextBlockId5 = string | null;
export type Blocks = UserFlowBlockConfig[];
export type X = number;
export type Y = number;
export type Id3 = number;
export type TgGroupChatType = "group" | "supergroup" | "channel";
export type Title = string;
export type Description = string | null;
export type Username = string | null;
export type IsForum = boolean | null;
export type Photo = string | null;
export type Id4 = number;
export type Username1 = string;
export type Name2 = string;
export type Description1 = string;
export type ShortDescription1 = string;
export type CanJoinGroups = boolean;
export type CanReadAllGroupMessages = boolean;
export type Command1 = string;
export type Description2 = string;
export type Commands = TgBotCommand[];
export type Userpic = string | null;
export type Name3 = string;
export type Description3 = string;
export type ShortDescription2 = string;
export type Code = string;
export type Name4 = string;
export type LocalName = string | null;
export type Emoji = string | null;
export type Id5 = string;
export type Name5 = string;
export type Prompt2 =
  | string
  | {
      [k: string]: string;
    };
export type IsRequired2 = boolean;
export type ResultFormatting2 = FormFieldResultFormattingOpts | "auto" | null;
export type AuthType = "no_auth" | "tg_group_auth" | "tg_auth";
export type Username2 = string;
export type Name6 = string;
export type DisplayUsername = string | null;
export type Userpic1 = string | null;
export type DisplayName1 = string;
export type CreatedAt = string;
export type LastUpdatedAt = string;
export type LastRunAt = string | null;
export type DeletedAt = string | null;
export type IsRunning = boolean;
export type VersionMessage = string | null;
export type Restart = boolean;
export type Version = number;

/**
 * Temporary class to pack several models into one schema; not used directly by frontend code
 */
export interface BackendDataModels {
  bot_config: BotConfig;
  tg_group_chat: TgGroupChat;
  tg_bot_user: TgBotUser;
  tg_bot_user_update: TgBotUserUpdate;
  language_data: LanguageData;
  base_form_field_config: BaseFormFieldConfig;
  logged_in_user: LoggedInUser;
  bot_info: BotInfo;
  save_bot_config_version_payload: SaveBotConfigVersionPayload;
  start_bot_payload: StartBotPayload;
  [k: string]: unknown;
}
export interface BotConfig {
  display_name: DisplayName;
  token_secret_name: TokenSecretName;
  user_flow_config: UserFlowConfig;
  [k: string]: unknown;
}
export interface UserFlowConfig {
  entrypoints: Entrypoints;
  blocks: Blocks;
  node_display_coords: NodeDisplayCoords;
  [k: string]: unknown;
}
export interface UserFlowEntryPointConfig {
  command?: CommandEntryPoint | null;
  catch_all?: CatchAllEntryPoint | null;
  regex?: RegexMatchEntryPoint | null;
  [k: string]: unknown;
}
/**
 * Basic entrypoint catching Telegram /commands
 */
export interface CommandEntryPoint {
  entrypoint_id: EntrypointId;
  command: Command;
  next_block_id: NextBlockId;
  scope?: CommandScope & string;
  short_description?: ShortDescription;
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
  content?: ContentBlock | null;
  human_operator?: HumanOperatorBlock | null;
  menu?: MenuBlock | null;
  form?: FormBlock | null;
  language_select?: LanguageSelectBlock | null;
  [k: string]: unknown;
}
/**
 * Simplest user flow block: static content sent by bot in one or several telegram messages.
 * Immediately continues to the next block after sending the content.
 */
export interface ContentBlock {
  block_id: BlockId;
  contents: Contents;
  next_block_id: NextBlockId3;
  [k: string]: unknown;
}
export interface Content {
  text: ContentText | null;
  attachments: Attachments;
  [k: string]: unknown;
}
export interface ContentText {
  text: Text;
  markup: ContentTextMarkup;
  [k: string]: unknown;
}
export interface ContentBlockContentAttachment {
  image: Image;
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
  [k: string]: unknown;
}
export interface Menu {
  text: Text1;
  items: Items;
  config: MenuConfig;
  [k: string]: unknown;
}
export interface MenuItem {
  label: Label;
  submenu?: Menu | null;
  next_block_id?: NextBlockId4;
  link_url?: LinkUrl;
  [k: string]: unknown;
}
export interface MenuConfig {
  mechanism: MenuMechanism;
  back_label: BackLabel;
  lock_after_termination: LockAfterTermination;
  [k: string]: unknown;
}
/**
 * Block with a series of questions to user with options to export their answers in various formats
 */
export interface FormBlock {
  block_id: BlockId3;
  form_name: FormName;
  members: Members;
  messages: FormMessages;
  results_export: FormResultsExport;
  form_completed_next_block_id: FormCompletedNextBlockId;
  form_cancelled_next_block_id: FormCancelledNextBlockId;
  [k: string]: unknown;
}
export interface BranchingFormMemberConfig {
  field?: FormFieldConfig | null;
  branch?: FormBranchConfig | null;
  [k: string]: unknown;
}
export interface FormFieldConfig {
  plain_text?: PlainTextFormFieldConfig | null;
  single_select?: SingleSelectFormFieldConfig | null;
  [k: string]: unknown;
}
export interface PlainTextFormFieldConfig {
  id: Id;
  name: Name;
  prompt: Prompt;
  is_required: IsRequired;
  result_formatting: ResultFormatting;
  is_long_text: IsLongText;
  empty_text_error_msg: EmptyTextErrorMsg;
  [k: string]: unknown;
}
export interface FormFieldResultFormattingOpts {
  descr: Descr;
  is_multiline?: IsMultiline;
  value_formatter?: ValueFormatter;
  [k: string]: unknown;
}
export interface SingleSelectFormFieldConfig {
  id: Id1;
  name: Name1;
  prompt: Prompt1;
  is_required: IsRequired1;
  result_formatting: ResultFormatting1;
  options: Options;
  invalid_enum_error_msg: InvalidEnumErrorMsg;
  [k: string]: unknown;
}
export interface EnumOption {
  id: Id2;
  label: Label1;
  [k: string]: unknown;
}
export interface FormBranchConfig {
  members: Members1;
  condition_match_value?: ConditionMatchValue;
  [k: string]: unknown;
}
export interface FormMessages {
  form_start: FormStart;
  cancel_command_is: CancelCommandIs;
  field_is_skippable: FieldIsSkippable;
  field_is_not_skippable: FieldIsNotSkippable;
  please_enter_correct_value: PleaseEnterCorrectValue;
  unsupported_command: UnsupportedCommand;
}
export interface FormResultsExport {
  echo_to_user: EchoToUser;
  is_anonymous: IsAnonymous;
  to_chat: FormResultsExportToChatConfig | null;
  [k: string]: unknown;
}
export interface FormResultsExportToChatConfig {
  chat_id: ChatId;
  via_feedback_handler: ViaFeedbackHandler;
  [k: string]: unknown;
}
/**
 * Language selection menu block. If specified, all texts in the containing user flow must be multilang
 * and be translated to all of the supported languages. Only one such block is permitted per user flow.
 */
export interface LanguageSelectBlock {
  block_id: BlockId4;
  menu_config: LanguageSelectionMenuConfig;
  supported_languages: SupportedLanguages;
  default_language: string;
  language_selected_next_block_id: LanguageSelectedNextBlockId;
  next_block_id?: NextBlockId5;
  [k: string]: unknown;
}
export interface LanguageSelectionMenuConfig {
  propmt: Propmt;
  is_blocking: IsBlocking;
  emoji_buttons: EmojiButtons;
  [k: string]: unknown;
}
export interface Propmt {
  [k: string]: string;
}
export interface NodeDisplayCoords {
  [k: string]: UserFlowNodePosition;
}
export interface UserFlowNodePosition {
  x: X;
  y: Y;
  [k: string]: unknown;
}
/**
 * pydantic projection of https://core.telegram.org/bots/api#chat
 */
export interface TgGroupChat {
  id: Id3;
  type: TgGroupChatType;
  title: Title;
  description: Description;
  username: Username;
  is_forum: IsForum;
  photo: Photo;
  [k: string]: unknown;
}
/**
 * Info on telegram bot, combining info from several Bot API endpoints
 */
export interface TgBotUser {
  id: Id4;
  username: Username1;
  name: Name2;
  description: Description1;
  short_description: ShortDescription1;
  can_join_groups: CanJoinGroups;
  can_read_all_group_messages: CanReadAllGroupMessages;
  commands: Commands;
  userpic: Userpic;
  [k: string]: unknown;
}
export interface TgBotCommand {
  command: Command1;
  description: Description2;
  [k: string]: unknown;
}
export interface TgBotUserUpdate {
  name: Name3;
  description: Description3;
  short_description: ShortDescription2;
  [k: string]: unknown;
}
export interface LanguageData {
  code: Code;
  name: Name4;
  local_name?: LocalName;
  emoji?: Emoji;
  [k: string]: unknown;
}
export interface BaseFormFieldConfig {
  id: Id5;
  name: Name5;
  prompt: Prompt2;
  is_required: IsRequired2;
  result_formatting: ResultFormatting2;
  [k: string]: unknown;
}
export interface LoggedInUser {
  auth_type: AuthType;
  username: Username2;
  name: Name6;
  display_username?: DisplayUsername;
  userpic?: Userpic1;
  [k: string]: unknown;
}
export interface BotInfo {
  display_name: DisplayName1;
  timestamps: BotTimestamps;
  is_running: IsRunning;
  [k: string]: unknown;
}
export interface BotTimestamps {
  created_at: CreatedAt;
  last_updated_at: LastUpdatedAt;
  last_run_at: LastRunAt;
  deleted_at: DeletedAt;
  [k: string]: unknown;
}
export interface SaveBotConfigVersionPayload {
  config: BotConfig;
  version_message: VersionMessage;
  restart: Restart;
  [k: string]: unknown;
}
export interface StartBotPayload {
  version: Version;
  [k: string]: unknown;
}
