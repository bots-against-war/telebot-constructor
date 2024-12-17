import { type Result } from "../utils";
import { apiUrl } from "./config";

export function paginationQuery(offset: number, count: number): string {
  return `offset=${encodeURIComponent(offset)}&count=${encodeURIComponent(count)}`;
}

/**
 * Thin wrapper around native Fetch API, handles URL prefixing and converts exceptions into Result type
 */
export async function fetchApi(input: string, init?: RequestInit): Promise<Result<Response>> {
  try {
    const response = await fetch(apiUrl(input), init);
    return { ok: true, data: response };
  } catch (err) {
    return {
      ok: false,
      error: err instanceof Error ? err.message : "Unknown fetch error",
    };
  }
}
