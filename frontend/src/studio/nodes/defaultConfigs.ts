import type { FormMessages, UserFlowBlockConfig, UserFlowEntryPointConfig } from "../../api/types";
import type { LanguageConfig } from "../stores";
import { updateWithPrefilled } from "./FormBlock/prefill";

export function defaultCommandEntrypoint(id: string): UserFlowEntryPointConfig {
  return {
    command: {
      entrypoint_id: id,
      command: "command",
      scope: "private",
      short_description: null,
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

export function defaultHumanOperatorBlockConfig(id: string): UserFlowBlockConfig {
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
          forwarded_to_admin_ok: "",
          throttling: "",
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

export function defaultMenuBlockConfig(id: string, langConfig: LanguageConfig | null): UserFlowBlockConfig {
  return {
    menu: {
      block_id: id,
      menu: {
        text: "",
        items: [],
        config: {
          back_label:
            langConfig === null
              ? "⬅️"
              : Object.fromEntries(langConfig.supportedLanguageCodes.map((lang) => [lang, "⬅️"])),
          mechanism: "inline_buttons",
          lock_after_termination: false,
        },
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

export function defaultFormBlockConfig(id: string, langConfig: LanguageConfig | null): UserFlowBlockConfig {
  let messages: FormMessages = {
    form_start: "",
    field_is_skippable: "",
    field_is_not_skippable: "",
    please_enter_correct_value: "",
    unsupported_command: "",
    cancel_command_is: "",
  };
  [messages] = updateWithPrefilled(messages, langConfig);
  return {
    form: {
      block_id: id,
      members: [],
      form_name: `form-${crypto.randomUUID()}`,
      messages: messages,
      results_export: {
        user_attribution: "none",
        echo_to_user: true,
        to_chat: null,
        to_store: false,
      },
      form_cancelled_next_block_id: null,
      form_completed_next_block_id: null,
    },
  };
}
