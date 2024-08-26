import { toTrivialResult, type Result, toDataResult } from "../utils";
import { apiUrl } from "./config";

export async function listSecrets(): Promise<Result<string[], string>> {
  const resp = await fetch(apiUrl(`/secrets`));
  return await toDataResult(resp);
}

export async function saveSecret(name: string, value: string): Promise<Result<null>> {
  const resp = await fetch(apiUrl(`/secrets/${encodeURIComponent(name)}`), {
    method: "POST",
    body: value,
  });
  return await toTrivialResult(resp);
}

export async function deleteSecret(name: string): Promise<Result<null>> {
  const resp = await fetch(apiUrl(`/secrets/${encodeURIComponent(name)}`), {
    method: "DELETE",
  });
  return await toTrivialResult(resp);
}
