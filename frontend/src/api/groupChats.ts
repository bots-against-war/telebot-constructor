import { toDataResult, toTrivialResult, type Result } from "../utils";
import type { TgGroupChat } from "./types";
import { fetchApi } from "./utils";

export async function getGroupChatData(botId: string, chatId: string | number): Promise<Result<TgGroupChat>> {
  const res = await fetchApi(`/group-chat/${encodeURIComponent(botId)}?group_chat=${encodeURIComponent(chatId)}`);
  return await toDataResult(res);
}

export async function getAvailableGroupChats(botId: string): Promise<Result<TgGroupChat[]>> {
  const res = await fetchApi(`/available-group-chats/${encodeURIComponent(botId)}`);
  return await toDataResult(res);
}

export async function startGroupChatDiscovery(botId: string): Promise<Result<null>> {
  const res = await fetchApi(`/start-group-chat-discovery/${encodeURIComponent(botId)}`, { method: "POST" });
  return await toTrivialResult(res);
}

export async function stopGroupChatDiscovery(botId: string): Promise<Result<null>> {
  const res = await fetchApi(`/stop-group-chat-discovery/${encodeURIComponent(botId)}`, { method: "POST" });
  return await toTrivialResult(res);
}
