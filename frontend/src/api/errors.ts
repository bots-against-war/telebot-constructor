import { toDataResult, type Result } from "../utils";
import type { BotErrorsPage } from "./types";
import { fetchApi, paginationQuery } from "./utils";

const encode = encodeURIComponent;

export async function loadErrors(botId: string, offset: number, count: number): Promise<Result<BotErrorsPage>> {
  const res = await fetchApi(`/errors/${encode(botId)}?${paginationQuery(offset, count)}`);
  return await toDataResult(res);
}
