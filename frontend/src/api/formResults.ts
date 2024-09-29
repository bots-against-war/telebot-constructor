import { err, ok, toDataResult, toTrivialResult, type Result } from "../utils";
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

export async function exportFormResults(
  botId: string,
  formBlockId: string,
  minDate: Date | null,
  maxDate: Date | null,
): Promise<Result<string>> {
  const toTimestamp = (d: Date) => Math.floor(+d / 1000);

  let queryParts = [];
  if (minDate !== null) {
    queryParts.push(`min_timestamp=${toTimestamp(minDate)}`);
  }
  if (maxDate !== null) {
    queryParts.push(`max_timestamp=${toTimestamp(maxDate)}`);
  }
  const query = queryParts.length > 0 ? "?" + queryParts.join("&") : "";
  const resp = await fetch(apiUrl(`/forms/${encode(botId)}/${encode(formBlockId)}/export${query}`));
  const respText = await resp.text();
  if (resp.ok) return ok(respText);
  else return err(respText);
}
