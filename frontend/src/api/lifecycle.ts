import { toDataResult, type Result, toTrivialResult } from "../utils";
import { apiUrl } from "./config";
import type { BotConfig } from "./types";

async function startBot(botName: string): Promise<Result<null>> {
  const resp = await fetch(apiUrl(`/start/${encodeURIComponent(botName)}`), {
    method: "POST",
  });
  return await toTrivialResult(resp);
}

async function stopBot(botName: string): Promise<Result<BotConfig>> {
  const resp = await fetch(apiUrl(`/stop/${encodeURIComponent(botName)}`), {
    method: "POST",
  });
  return await toTrivialResult(resp);
}

async function listRunningBots(): Promise<Result<string[]>> {
  const resp = await fetch(apiUrl(`/running`), {});
  return await toDataResult(resp);
}
