import { getContext, type ComponentProps } from "svelte";
import { type SvelteComponent } from "svelte";
import type { Newable } from "ts-essentials";

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
    // @ts-ignore
    throw new Error(result.error);
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

export function mean(data: number[]): number {
  if (data.length < 1) {
    return NaN;
  }
  return data.reduce((prev, current) => prev + current) / data.length;
}

// returns typed version of svelte-simple-modals open func
export function getModalOpener<C extends SvelteComponent>(): (
  // wtf? https://github.com/sveltejs/language-tools/issues/486#issuecomment-1101614455
  modalCompClass: Newable<C>,
  props?: ComponentProps<C>,
) => void {
  // @ts-ignore
  const { open } = getContext("simple-modal");
  return open;
}

// returns typed version of svelte-simple-modals open func
export function getModalCloser(): () => void {
  // @ts-ignore
  const { close } = getContext("simple-modal");
  return close;
}
