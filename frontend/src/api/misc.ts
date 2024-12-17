import type { PrefilledMessages } from "../studio/nodes/FormBlock/prefill";
import { toDataResult, type Result } from "../utils";
import type { LanguageData, LoggedInUser } from "./types";
import { fetchApi } from "./utils";

export async function getAvailableLanguages(): Promise<Result<LanguageData[]>> {
  const res = await fetchApi(`/all-languages`);
  return await toDataResult(res);
}

export async function fetchPrefilledMessages(): Promise<Result<PrefilledMessages>> {
  const res = await fetchApi(`/prefilled-messages`);
  return await toDataResult(res);
}

export async function getLoggedInUser(): Promise<Result<LoggedInUser>> {
  const res = await fetchApi(`/logged-in-user`);
  return await toDataResult(res);
}
