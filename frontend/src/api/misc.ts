import type { PrefillableMessages } from "../studio/nodes/FormBlock/prefill";
import { toDataResult, type Result } from "../utils";
import { apiUrl } from "./config";
import type { LanguageData } from "./types";

export async function getAvailableLanguages(): Promise<Result<LanguageData[]>> {
  const resp = await fetch(apiUrl(`/all-languages`));
  return await toDataResult(resp);
}

export async function fetchPrefilledMessages(): Promise<Result<PrefillableMessages>> {
  const resp = await fetch(apiUrl(`/prefilled-messages`));
  return await toDataResult(resp);
}
