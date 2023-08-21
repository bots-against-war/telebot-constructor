// rust-like result type with convenience functions

export type Result<T, E = string> = { data: T; ok: true } | { error: E; ok: false };

export function ok<T, E = string>(data: T): Result<T, E> {
  return { data, ok: true };
}

export function err<T, E = string>(error: E): Result<T, E> {
  return { error, ok: false };
}

export function unwrap<T, E = string>(result: Result<T, E>): T {
  if (result.ok) {
    return result.data;
  } else {
    throw new Error(result.error); // @ts-ignore
  }
}

export async function toTrivialResult(resp: Response): Promise<Result<null, string>> {
  if (resp.ok) return ok(null);
  else return err(await resp.text());
}

export async function toDataResult<T>(resp: Response): Promise<Result<T, string>> {
  const respText = await resp.text();
  if (resp.ok) return ok(JSON.parse(respText));
  else return err(respText);
}
