import type { BotInfo } from "./types";
import { type Result, toDataResult } from "../utils";
import { apiUrl } from "./config";

export async function saveBotInfo(botName: string, info: BotInfo): Promise<Result<BotInfo>> {
  const resp = await fetch(apiUrl(`/bots/info/${encodeURIComponent(botName)}`), {
    method: "POST",
    body: JSON.stringify(info),
  });

  return await toDataResult(resp);
}

export async function loadBotsInfo(): Promise<Result<{ [key: string]: BotInfo }>> {
  const resp = await fetch(apiUrl(`/bots/info`));

  return await toDataResult(resp);
}
