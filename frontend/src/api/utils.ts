export function paginationQuery(offset: number, count: number): string {
  return `offset=${encodeURIComponent(offset)}&count=${encodeURIComponent(count)}`;
}
