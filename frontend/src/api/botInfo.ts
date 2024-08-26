import type { BotInfo } from "./types";
import { type Result, toDataResult } from "../utils";
import { apiUrl } from "./config";

export async function getBotInfo(botId: string): Promise<Result<BotInfo>> {
  const resp = await fetch(apiUrl(`/info/${encodeURIComponent(botId)}`));
  return await toDataResult(resp);
}

export async function listBotInfos(): Promise<Result<BotInfo[]>> {
  const resp = await fetch(apiUrl(`/info?detailed=false`));
  return await toDataResult(resp);
}
