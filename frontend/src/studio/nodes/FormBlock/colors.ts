import { md5 } from "js-md5";
import { range } from "../../utils";

export function generateHue(seed: string, index: number): number {
  const startHue = new Uint16Array(md5.arrayBuffer(seed))[0] % 360;
  if (index === 0) return startHue;
  let currentIndex = 0;
  let power = 0;
  while (true) {
    power += 1;
    const denominator = 2 ** power;
    const numOffset = denominator / 2;
    const numStart = 1;
    const numStep = 2;
    const numCount = denominator / 2;
    for (const numerator of range(numCount, numStart, numStep)) {
      if (currentIndex >= index) {
        const result = (startHue + (360 * (numOffset + numerator)) / denominator) % 360;
        return result;
      }
      currentIndex += 1;
    }
  }
}

export function borderColor(hue: number): string {
  return `hsl(${hue}, 60%, 80%)`;
}

export function backgroundColor(hue: number): string {
  return `hsl(${hue}, 60%, 80%)`;
}
