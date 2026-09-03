import { getAccessToken } from "./cloudbaseClient";
import { getVisitorId } from "../utils/visitorId";

export class AccessCodeRequiredError extends Error {
  constructor(message = "请输入访问口令") {
    super(message);
    this.name = "AccessCodeRequiredError";
  }
}

export function throwIfAccessCodeRequired(text: string, status: number): void {
  if (status !== 401) {
    return;
  }
  try {
    const data = JSON.parse(text) as { detail?: { code?: string; message?: string } | string };
    if (
      data.detail &&
      typeof data.detail === "object" &&
      data.detail.code === "access_code_required"
    ) {
      throw new AccessCodeRequiredError(data.detail.message || "请输入访问口令");
    }
  } catch (err) {
    if (err instanceof AccessCodeRequiredError) {
      throw err;
    }
  }
}

/** Fast headers for chart/paipan APIs that do not require login. */
export function jsonPublicHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "X-Device-Id": getVisitorId(),
  };
  const code = window.localStorage.getItem("zy_access_code");
  if (code) {
    headers["X-Access-Code"] = code;
  }
  return headers;
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
  const detail = parseDetailMessage(text);
  if (detail) {
    return detail;
  }
  if (status === 401) {
    return "请求未授权";
  }
  if (status === 402) {
    return "今日 AI 次数已用完, 明日再试";
  }
  return text.trim() || `Request failed: ${status}`;
}

export function parseQuotaError(text: string, status: number): string {
  return parseApiErrorMessage(text, status);
}
