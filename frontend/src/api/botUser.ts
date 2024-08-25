import { toDataResult, toTrivialResult, type Result } from "../utils";
import { apiUrl } from "./config";
import type { TgBotUser, TgBotUserUpdate } from "./types";

export async function getBotUser(botId: string): Promise<Result<TgBotUser>> {
  const resp = await fetch(apiUrl(`/bot-user/${encodeURIComponent(botId)}`));
  return await toDataResult(resp);
}

export async function updateBotUser(botId: string, update: TgBotUserUpdate): Promise<Result<null>> {
  const resp = await fetch(apiUrl(`/bot-user/${encodeURIComponent(botId)}`), {
    method: "PUT",
    body: JSON.stringify(update),
  });
  return await toTrivialResult(resp);
}
