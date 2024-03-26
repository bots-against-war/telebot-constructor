import { type Result, toTrivialResult } from "../utils";
import { apiUrl } from "./config";
import type { StartBotPayload } from "./types";

export async function startBot(botName: string, payload: StartBotPayload): Promise<Result<null>> {
  const resp = await fetch(apiUrl(`/start/${encodeURIComponent(botName)}`), {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return await toTrivialResult(resp);
}

export async function stopBot(botName: string): Promise<Result<null>> {
  const resp = await fetch(apiUrl(`/stop/${encodeURIComponent(botName)}`), {
    method: "POST",
  });
  return await toTrivialResult(resp);
}
