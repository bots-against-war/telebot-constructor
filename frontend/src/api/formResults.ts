import { toDataResult, type Result } from "../utils";
import { apiUrl } from "./config";
import type { FormResultsPage } from "./types";

const encode = encodeURIComponent;

export async function getFormResults(
  botId: string,
  formBlockId: string,
  offset: number,
  count: number,
): Promise<Result<FormResultsPage>> {
  const resp = await fetch(
    apiUrl(
      `/forms/${encode(botId)}/${encode(formBlockId)}/responses` + `?offset=${encode(offset)}&count=${encode(count)}`,
    ),
  );
  return await toDataResult(resp);
}
