import { type Result, toTrivialResult } from "../utils";
import type { StartBotPayload } from "./types";
import { fetchApi } from "./utils";

export async function startBot(botId: string, payload: StartBotPayload): Promise<Result<null>> {
  const res = await fetchApi(`/start/${encodeURIComponent(botId)}`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return await toTrivialResult(res);
}

export async function stopBot(botId: string): Promise<Result<null>> {
  const res = await fetchApi(`/stop/${encodeURIComponent(botId)}`, {
    method: "POST",
  });
  return await toTrivialResult(res);
}
