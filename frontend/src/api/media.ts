import { type Result, toStringResult, toTrivialResult } from "../utils";
import { apiUrl } from "./config";

const encode = encodeURIComponent;

export async function saveMedia(file: File, forBotId: string): Promise<Result<string>> {
  const resp = await fetch(apiUrl(`/media?bot_id=${encode(forBotId)}`), {
    method: "POST",
    body: file,
    headers: {
      "X-Telebot-Constructor-Filename": file.name,
    },
  });
  return await toStringResult(resp);
}

export function mediaUrl(mediaId: string, forBotId: string): string {
  return apiUrl(`/media/${encode(mediaId)}/?bot_id=${encode(forBotId)}`);
}

export async function deleteMedia(mediaId: string, forBotId: string): Promise<Result<null>> {
  const resp = await fetch(apiUrl(`/media/${encode(mediaId)}?bot_id=${encode(forBotId)}`), {
    method: "DELETE",
  });
  return await toTrivialResult(resp);
}
