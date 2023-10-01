import { toTrivialResult, type Result } from "../utils";
import { apiUrl } from "./config";

export async function validateBotToken(token: string): Promise<Result<null, string>> {
  const resp = await fetch(apiUrl(`/validate-token`), { method: "POST", body: JSON.stringify({ token }) });
  return await toTrivialResult(resp);
}
