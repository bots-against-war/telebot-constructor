import type { BotInfo, BotVersionsPage } from "./types";
import { type Result, toDataResult, toTrivialResult } from "../utils";
import { apiUrl } from "./config";
import { paginationQuery } from "./utils";

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

export async function getBotVersionsPage(
  botId: string,
  offset: number,
  count: number,
): Promise<Result<BotVersionsPage>> {
  const resp = await fetch(apiUrl(`/info/${encodeURIComponent(botId)}/versions?${paginationQuery(offset, count)}`));
  return await toDataResult(resp);
}
