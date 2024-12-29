import { toStringResult, toTrivialResult, type Result } from "../utils";
import { apiUrl } from "./config";
import { fetchApi } from "./utils";

const encode = encodeURIComponent;

export async function saveMedia(file: File, forBotId: string): Promise<Result<string>> {
  const res = await fetchApi(`/media?bot_id=${encode(forBotId)}`, {
    method: "POST",
    body: file,
    headers: {
      "X-Telebot-Constructor-Filename": encodeURIComponent(file.name),
    },
  });
  return await toStringResult(res);
}

export function mediaUrl(mediaId: string, forBotId: string): string {
  return apiUrl(`/media/${encode(mediaId)}?bot_id=${encode(forBotId)}`);
}

export async function deleteMedia(mediaId: string, forBotId: string): Promise<Result<null>> {
  const res = await fetchApi(`/media/${encode(mediaId)}?bot_id=${encode(forBotId)}`, {
    method: "DELETE",
  });
  return await toTrivialResult(res);
}
