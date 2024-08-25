import { type Result, toTrivialResult } from "../utils";
import { apiUrl } from "./config";
import type { StartBotPayload } from "./types";

export async function startBot(botId: string, payload: StartBotPayload): Promise<Result<null>> {
  const resp = await fetch(apiUrl(`/start/${encodeURIComponent(botId)}`), {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return await toTrivialResult(resp);
}

export async function stopBot(botId: string): Promise<Result<null>> {
  const resp = await fetch(apiUrl(`/stop/${encodeURIComponent(botId)}`), {
    method: "POST",
  });
  return await toTrivialResult(resp);
}
