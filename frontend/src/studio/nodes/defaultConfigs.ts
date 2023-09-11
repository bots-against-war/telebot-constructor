import type { UserFlowBlockConfig, UserFlowEntryPointConfig } from "../../api/types";

export function defaultCommandEntrypoint(id: string): UserFlowEntryPointConfig {
  return {
    command: {
      entrypoint_id: id,
      command: "command",
      next_block_id: null,
    },
  };
}

export function defaultMessageBlockConfig(id: string): UserFlowBlockConfig {
  return {
    message: {
      block_id: id,
      message_text: "Hello, I am bot!",
      next_block_id: null,
    },
    human_operator: null,
  };
}

export function defaultHumanOperatorBlockCofig(id: string): UserFlowBlockConfig {
  return {
    message: null,
    human_operator: {
      block_id: id,
      catch_all: false,
      feedback_handler_config: {
        admin_chat_id: -1,
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
