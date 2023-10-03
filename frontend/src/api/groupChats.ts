import { toDataResult, type Result } from "../utils";
import { apiUrl } from "./config";
import type { TgGroupChat } from "./types";

export async function getGroupChatData(botName: string, chatId: string | number): Promise<Result<TgGroupChat>> {
  const resp = await fetch(
    apiUrl(`/group-chat/${encodeURIComponent(botName)}?group_chat=${encodeURIComponent(chatId)}`),
  );
  return await toDataResult(resp);
}
