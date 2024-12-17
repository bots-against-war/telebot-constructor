import { toDataResult, toStringResult, toTrivialResult, type Result } from "../utils";
import type { FormResultsPage } from "./types";
import { fetchApi, paginationQuery } from "./utils";

const encode = encodeURIComponent;

export async function loadFormResults(
  botId: string,
  formBlockId: string,
  offset: number,
  count: number,
): Promise<Result<FormResultsPage>> {
  const res = await fetchApi(
    `/forms/${encode(botId)}/${encode(formBlockId)}/responses?${paginationQuery(offset, count)}`,
  );
  return await toDataResult(res);
}

export async function updateFormTitle(botId: string, formBlockId: string, newTitle: string): Promise<Result<null>> {
  const res = await fetchApi(`/forms/${encode(botId)}/${encode(formBlockId)}/title`, {
    method: "PUT",
    body: newTitle,
  });
  return await toTrivialResult(res);
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
  const res = await fetchApi(`/forms/${encode(botId)}/${encode(formBlockId)}/export${query}`);
  return toStringResult(res);
}
