import { toDataResult, toTrivialResult, type Result } from "../utils";
import type { BotErrorsPage, SetAlertChatIdPayload } from "./types";
import { fetchApi, paginationQuery } from "./utils";

const encode = encodeURIComponent;

export async function loadErrors(botId: string, offset: number, count: number): Promise<Result<BotErrorsPage>> {
  const res = await fetchApi(`/errors/${encode(botId)}?${paginationQuery(offset, count)}`);
  return await toDataResult(res);
}

export async function setAlertChatId(botId: string, payload: SetAlertChatIdPayload): Promise<Result<null>> {
  const res = await fetchApi(`/alert-chat-id/${encode(botId)}`, {
    method: "POST",
    body: JSON.stringify(payload),
    headers: {
      "Content-Type": "application/json",
    },
  });
  return await toTrivialResult(res);
}

export async function removeAlertChatId(botId: string): Promise<Result<null>> {
  const res = await fetchApi(`/alert-chat-id/${encode(botId)}`, {
    method: "DELETE",
  });
  return await toTrivialResult(res);
}
