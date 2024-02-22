import { toDataResult, type Result, toTrivialResult } from "../utils";
import { apiUrl } from "./config";

export async function startBot(botName: string): Promise<Result<null>> {
  const resp = await fetch(apiUrl(`/start/${encodeURIComponent(botName)}`), {
    method: "POST",
  });
  return await toTrivialResult(resp);
}

export async function stopBot(botName: string): Promise<Result<null>> {
  const resp = await fetch(apiUrl(`/stop/${encodeURIComponent(botName)}`), {
    method: "POST",
  });
  return await toTrivialResult(resp);
}
