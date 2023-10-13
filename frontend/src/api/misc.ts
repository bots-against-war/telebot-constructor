import { toDataResult, type Result } from "../utils";
import { apiUrl } from "./config";
import type { LanguageData } from "./types";

export async function getAvailableLanguages(): Promise<Result<LanguageData[]>> {
  const resp = await fetch(apiUrl(`/all-languages`));
  return await toDataResult(resp);
}
