import { getAccessToken } from "./cloudbaseClient";
import { getVisitorId } from "../utils/visitorId";

/** Fast headers for chart/paipan APIs that do not require login. */
export function jsonPublicHeaders(): Record<string, string> {
  return {
    "Content-Type": "application/json",
    "X-Device-Id": getVisitorId(),
  };
}

export async function jsonDeviceHeaders(modelId?: string): Promise<Record<string, string>> {
  const headers: Record<string, string> = {
    ...jsonPublicHeaders(),
  };
  if (modelId?.trim()) {
    headers["X-Model-Id"] = modelId.trim();
  }
  const token = await getAccessToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

function parseDetailMessage(text: string): string | null {
  try {
    const data = JSON.parse(text) as { detail?: { message?: string } | string };
    if (typeof data.detail === "object" && data.detail?.message) {
      return data.detail.message;
    }
    if (typeof data.detail === "string") {
      return data.detail;
    }
  } catch {
    /* ignore */
  }
  return null;
}

export function parseApiErrorMessage(text: string, status: number): string {
  if (status === 401) {
    return "请先登录后再使用 AI 功能";
  }
  const detail = parseDetailMessage(text);
  if (detail) {
    return detail;
  }
  if (status === 402) {
    return "今日 AI 次数已用完, 请兑换秘钥或明日再试";
  }
  return text.trim() || `Request failed: ${status}`;
}

export function parseQuotaError(text: string, status: number): string {
  return parseApiErrorMessage(text, status);
}
