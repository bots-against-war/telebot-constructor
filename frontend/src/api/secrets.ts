import { toTrivialResult, type Result, ok, err } from "../utils";
import { apiUrl } from "./config";

export async function listSecrets(): Promise<Result<string[], string>> {
  const resp = await fetch(apiUrl(`/api/secrets`));
  const respText = await resp.text();
  if (resp.ok) {
    return ok(JSON.parse(respText));
  } else {
    return err(respText);
  }
}

export async function createSecret(name: string, value: string): Promise<Result<null>> {
  const resp = await fetch(apiUrl(`/api/secrets/${encodeURIComponent(name)}`), {
    method: "POST",
    body: value,
  });
  return await toTrivialResult(resp);
}

export async function deleteSecret(name: string): Promise<Result<null>> {
  const resp = await fetch(apiUrl(`/api/secrets/${encodeURIComponent(name)}`), {
    method: "DELETE",
  });
  return await toTrivialResult(resp);
}
