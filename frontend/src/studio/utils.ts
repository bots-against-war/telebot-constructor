export function svelvetNodeIdToBlockId(id: string): string {
  // svelvet adds "N-" prefix to ids we pass to them, so we need to strip id back
  // see https://svelvet.mintlify.app/components/node#props
  return id.replace(/^N-/, "");
}
