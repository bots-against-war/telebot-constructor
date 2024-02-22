import type { BotInfo } from "./types";
import { type Result, toDataResult } from "../utils";
import { apiUrl } from "./config";

export async function getBotInfo(botName: string): Promise<Result<BotInfo>> {
  const resp = await fetch(apiUrl(`/info/${encodeURIComponent(botName)}`));

  return await toDataResult(resp);
}

export async function listBotInfos(): Promise<Result<{ [key: string]: BotInfo }>> {
  const resp = await fetch(apiUrl(`/info`));

  return await toDataResult(resp);
}
