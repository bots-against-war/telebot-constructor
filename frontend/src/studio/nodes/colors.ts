export const HUE = {
  command: 60,
  content: 197,
  human_operator: 77,
  language_select: 329,
};

export function headerColor(hue: number): string {
  return `hsl(${hue}, 70%, 70%)`;
}

export function buttonColor(hue: number): string {
  return `hsl(${hue}, 60%, 30%)`;
}
