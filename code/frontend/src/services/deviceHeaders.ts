import { getVisitorId } from "../utils/visitorId";

export function jsonDeviceHeaders(modelId?: string): Record<string, string> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "X-Device-Id": getVisitorId(),
  };
  if (modelId?.trim()) {
    headers["X-Model-Id"] = modelId.trim();
  }
  return headers;
}

export function parseQuotaError(text: string, status: number): string {
  if (status !== 402) {
    return text;
  }
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
  return "今日 AI 次数已用完, 请兑换秘钥或明日再试";
}
