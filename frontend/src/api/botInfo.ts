import type { BotInfo } from "./types";
import { type Result, toDataResult, toTrivialResult } from "../utils";
import { apiUrl } from "./config";

export async function getBotInfo(botId: string): Promise<Result<BotInfo>> {
  const resp = await fetch(apiUrl(`/info/${encodeURIComponent(botId)}`));
  return await toDataResult(resp);
}

export async function listBotInfos(): Promise<Result<BotInfo[]>> {
  const resp = await fetch(apiUrl(`/info?detailed=false`));
  return await toDataResult(resp);
}

export async function updateBotDisplayName(botId: string, newDisplayName: string): Promise<Result<null>> {
  const resp = await fetch(apiUrl(`/display-name/${botId}`), {
    method: "PUT",
    body: JSON.stringify({ display_name: newDisplayName }),
  });
  return await toTrivialResult(resp);
}
