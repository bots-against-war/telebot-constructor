import { toDataResult, toTrivialResult, type Result } from "../utils";
import { apiUrl } from "./config";
import type { FormResultsPage } from "./types";
import { paginationQuery } from "./utils";

const encode = encodeURIComponent;

export async function loadFormResults(
  botId: string,
  formBlockId: string,
  offset: number,
  count: number,
): Promise<Result<FormResultsPage>> {
  const resp = await fetch(
    apiUrl(`/forms/${encode(botId)}/${encode(formBlockId)}/responses?${paginationQuery(offset, count)}`),
  );
  return await toDataResult(resp);
}

export async function updateFormTitle(botId: string, formBlockId: string, newTitle: string): Promise<Result<null>> {
  const resp = await fetch(apiUrl(`/forms/${encode(botId)}/${encode(formBlockId)}/title`), {
    method: "PUT",
    body: newTitle,
  });
  return await toTrivialResult(resp);
}
