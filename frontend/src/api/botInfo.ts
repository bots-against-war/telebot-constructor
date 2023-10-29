import type { BotInfo } from "./types";
import { type Result, toDataResult } from "../utils";
import { apiUrl } from "./config";

export async function loadBotsInfo(): Promise<Result<{ [key: string]: BotInfo }>> {
  const resp = await fetch(apiUrl(`/bots/info`));

  return await toDataResult(resp);
}
