import { toDataResult, toTrivialResult, type Result } from "../utils";
import { apiUrl } from "./config";
import type { TgGroupChat } from "./types";

export async function getGroupChatData(botId: string, chatId: string | number): Promise<Result<TgGroupChat>> {
  const resp = await fetch(apiUrl(`/group-chat/${encodeURIComponent(botId)}?group_chat=${encodeURIComponent(chatId)}`));
  return await toDataResult(resp);
}

export async function getAvailableGroupChats(botId: string): Promise<Result<TgGroupChat[]>> {
  const resp = await fetch(apiUrl(`/available-group-chats/${encodeURIComponent(botId)}`));
  return await toDataResult(resp);
}

export async function startGroupChatDiscovery(botId: string): Promise<Result<null>> {
  const resp = await fetch(apiUrl(`/start-group-chat-discovery/${encodeURIComponent(botId)}`), { method: "POST" });
  return await toTrivialResult(resp);
}

export async function stopGroupChatDiscovery(botId: string): Promise<Result<null>> {
  const resp = await fetch(apiUrl(`/stop-group-chat-discovery/${encodeURIComponent(botId)}`), { method: "POST" });
  return await toTrivialResult(resp);
}
