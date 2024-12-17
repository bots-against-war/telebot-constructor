import { toDataResult, toTrivialResult, type Result } from "../utils";
import type { TgBotUser, TgBotUserUpdate } from "./types";
import { fetchApi } from "./utils";

export async function getBotUser(botId: string): Promise<Result<TgBotUser>> {
  const res = await fetchApi(`/bot-user/${encodeURIComponent(botId)}`);
  return await toDataResult(res);
}

export async function updateBotUser(botId: string, update: TgBotUserUpdate): Promise<Result<null>> {
  const res = await fetchApi(`/bot-user/${encodeURIComponent(botId)}`, {
    method: "PUT",
    body: JSON.stringify(update),
  });
  return await toTrivialResult(res);
}
