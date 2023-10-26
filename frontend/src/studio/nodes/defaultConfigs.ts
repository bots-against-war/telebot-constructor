import type { UserFlowBlockConfig, UserFlowEntryPointConfig } from "../../api/types";

export function defaultCommandEntrypoint(id: string): UserFlowEntryPointConfig {
  return {
    command: {
      entrypoint_id: id,
      command: "command",
      scope: "private",
      short_description: "Some command",
      next_block_id: null,
    },
  };
}

export function defaultContentBlockConfig(id: string): UserFlowBlockConfig {
  return {
    content: {
      block_id: id,
      contents: [{ text: { text: "Hello, I'm bot!", markup: "none" }, attachments: [] }],
      next_block_id: null,
    },
  };
}

export const PLACEHOLDER_GROUP_CHAT_ID = 0;

export function defaultHumanOperatorBlockCofig(id: string): UserFlowBlockConfig {
  return {
    human_operator: {
      block_id: id,
      catch_all: false,
      feedback_handler_config: {
        admin_chat_id: PLACEHOLDER_GROUP_CHAT_ID,
        forum_topic_per_user: false,
        anonimyze_users: true,
        max_messages_per_minute: 20,
        messages_to_user: {
          forwarded_to_admin_ok: "Message accepted!",
          throttling: "Please don't send more than {} messages in {}",
        },
        messages_to_admin: {
          copied_to_user_ok: "Copied to user",
          deleted_message_ok: "Message deleted from chat with user",
          can_not_delete_message: "Can't delete message from chat with user",
        },
        hashtags_in_admin_chat: false,
        hashtag_message_rarer_than: null,
        unanswered_hashtag: null,
        message_log_to_admin_chat: true,
      },
    },
  };
}

export function defaultLanguageSelectBlockConfig(id: string): UserFlowBlockConfig {
  return {
    language_select: {
      block_id: id,
      menu_config: {
        propmt: {},
        is_blocking: false,
        emoji_buttons: true,
      },
      supported_languages: [],
      default_language: "",
      language_selected_next_block_id: null,
    },
  };
}

export function defaultFormBlockConfig(id: string): UserFlowBlockConfig {
  return {
    form: {
      block_id: id,
      members: [],
      form_name: `form-${crypto.randomUUID()}`,
      messages: {
        form_start: "",
        field_is_skippable: "",
        field_is_not_skippable: "",
        please_enter_correct_value: "",
        unsupported_command: "",
      },
      results_export: {
        echo_to_user: true,
        is_anonymous: true,
        to_chat: {
          chat_id: PLACEHOLDER_GROUP_CHAT_ID,
          via_feedback_handler: true,
        },
      },
      form_cancelled_next_block_id: null,
      form_completed_next_block_id: null,
    },
  };
}
