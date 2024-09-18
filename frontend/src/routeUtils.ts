import { navigate } from "svelte-routing";

export const BASE_PATH = import.meta.env.BASE_URL || "";

export function navigateWithBasepath(to: string) {
  navigate(BASE_PATH + to);
}

function encodePathPart(part: any): any {
  if (typeof part !== "string") {
    return part;
  }
  // :identifier is a syntax used to render templates for svelte-simple-routing
  return part.at(0) === ":" ? part : encodeURIComponent(part);
}

export function formResultsPagePath(botId: string, formBlockId: string): string {
  return `/forms/${encodePathPart(botId)}/${encodePathPart(formBlockId)}`;
}

export function studioPath(botId: string, version: number | null): string {
  let path = `/studio/${encodePathPart(botId)}`;
  if (version !== null) {
    path += `?version=${encodePathPart(version)}`;
  }
  return path;
}

export function dashboardPath(botId: string): string {
  return `/dashboard/${encodePathPart(botId)}`;
}

export function botListingPath(): string {
  return "/bots";
}

export function versionsPagePath(botId: string): string {
  return `/versions/${encodePathPart(botId)}`;
}

export function settingsPath(botId: string): string {
  return `/settings/${encodePathPart(botId)}`;
}
