import { toDataResult, type Result } from "../utils";
import { apiUrl } from "./config";
import type { BotConfig, SaveBotConfigVersionPayload } from "./types";

export async function saveBotConfig(botName: string, payload: SaveBotConfigVersionPayload): Promise<Result<BotConfig>> {
  const resp = await fetch(apiUrl(`/config/${encodeURIComponent(botName)}`), {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return await toDataResult(resp);
}

export async function loadBotConfig(botName: string): Promise<Result<BotConfig>> {
  const resp = await fetch(apiUrl(`/config/${encodeURIComponent(botName)}`));
  return await toDataResult(resp);
}

export async function deleteBotConfig(botName: string): Promise<Result<BotConfig>> {
  const resp = await fetch(apiUrl(`/config/${encodeURIComponent(botName)}`), { method: "DELETE" });
  return await toDataResult(resp);
}
