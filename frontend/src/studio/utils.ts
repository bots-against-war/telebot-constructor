import type { UserFlowNodePosition } from "../api/types";
import type { LocalizableText } from "../types";
import type { LanguageConfig } from "./stores";

export function svelvetNodeIdToBlockId(id: string): string {
  // svelvet adds "N-" prefix to ids we pass to them, so we need to strip id back
  // see https://svelvet.mintlify.app/components/node#props
  return id.replace(/^N-/, "");
}

export function findNewNodePosition(
  current: UserFlowNodePosition[],
  nodeWidth: number,
  nodeHeight: number,
  margin: number,
): UserFlowNodePosition {
  const yMin = Math.min(...current.map(({ _, y }) => y));

  function yMax(x: number): number {
    return Math.max(
      yMin,
      ...current
        .filter(
          (nodePosition) => nodePosition.x > x - nodeWidth / 2 - margin && nodePosition.x < x + nodeWidth / 2 + margin,
        )
        .map((nodePosition) => nodePosition.y + nodeHeight + margin),
    );
  }

  const leftEdgeMin = Math.min(...current.map((pos) => pos.x)) - nodeWidth / 2;
  const leftEdgeMax = Math.max(...current.map((pos) => pos.x)) - nodeWidth / 2;
  const leftEdgeVariants = linspace(leftEdgeMin, leftEdgeMax, 8).map((v) => v + gaussianRandom(0, margin));
  const leftEdgeOptimalVariantIdx = argmin(leftEdgeVariants.map((x) => Math.max(yMax(x), yMax(x + nodeWidth))));
  const xOptimal = leftEdgeVariants[leftEdgeOptimalVariantIdx] + nodeWidth / 2;
  return {
    x: xOptimal,
    y: yMax(xOptimal),
  };
}

function linspace(start: number, stop: number, len: number): number[] {
  if (len === 0) {
    return [];
  } else if (len === 1) {
    return [start];
  }

  const out = new Array(len);
  out[0] = start;

  const delta = (stop - start) / (len - 1);
  for (let i = 1; i < len; i++) {
    out[i] = start + delta * i;
  }

  return out;
}

function argmin(arr: number[]): number {
  return argmax(arr.map((v) => -v));
}

function argmax(arr: number[]): number {
  if (arr.length === 0) {
    return -1;
  }

  let max = arr[0];
  let maxIndex = 0;

  for (let i = 1; i < arr.length; i++) {
    if (arr[i] > max) {
      maxIndex = i;
      max = arr[i];
    }
  }

  return maxIndex;
}

function gaussianRandom(mean: number, stdev: number) {
  const u = 1 - Math.random(); // Converting [0,1) to (0,1]
  const v = Math.random();
  const z = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
  // Transform to the desired mean and standard deviation:
  return z * stdev + mean;
}

export function base64Image(b64: string): string {
  return `data:image/png;base64,${b64}`;
}

export function capitalize(string: string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

// for display purposes only
export function localizableTextToString(lc: LocalizableText, langConfig: LanguageConfig | null): string {
  if (langConfig === null && typeof lc === 'string') return lc;
  else if (langConfig !== null && typeof lc === 'object') return lc[langConfig.defaultLanguageCode] || ""
  else return ""
}
