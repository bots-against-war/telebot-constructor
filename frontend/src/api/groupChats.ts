import { toDataResult, toTrivialResult, type Result, ok } from "../utils";
import { apiUrl } from "./config";
import type { TgGroupChat } from "./types";

export async function getGroupChatData(botName: string, chatId: string | number): Promise<Result<TgGroupChat>> {
  const resp = await fetch(
    apiUrl(`/group-chat/${encodeURIComponent(botName)}?group_chat=${encodeURIComponent(chatId)}`),
  );
  return await toDataResult(resp);
}

export async function getAvailableGroupChats(botName: string): Promise<Result<TgGroupChat[]>> {
  const resp = await fetch(apiUrl(`/available-group-chats/${encodeURIComponent(botName)}`));
  return await toDataResult(resp);
}

export async function startGroupChatDiscovery(botName: string): Promise<Result<null>> {
  const resp = await fetch(apiUrl(`/start-group-chat-discovery/${encodeURIComponent(botName)}`), { method: "POST" });
  return await toTrivialResult(resp);
}

export async function stopGroupChatDiscovery(botName: string): Promise<Result<null>> {
  const resp = await fetch(apiUrl(`/stop-group-chat-discovery/${encodeURIComponent(botName)}`), { method: "POST" });
  return await toTrivialResult(resp);
}
