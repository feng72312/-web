import { API_BASE } from "./config";
import { parseResponseJson } from "./httpJson";

const TOKEN_KEY = "bazi_admin_token_v1";

export function getAdminToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setAdminToken(token: string | null): void {
  if (!token) {
    localStorage.removeItem(TOKEN_KEY);
    return;
  }
  localStorage.setItem(TOKEN_KEY, token);
}

function authHeaders(): HeadersInit {
  const token = getAdminToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function parseError(response: Response): Promise<string> {
  if (response.status === 404) {
    return "接口不存在(404), 请确认后端已重启或已部署最新版本";
  }
  const text = await response.text();
  const trimmed = text.trim();
  if (trimmed.startsWith("<")) {
    return "请求到了网页而非接口, 请 Ctrl+F5 强刷后重试, 或确认 API 地址配置正确";
  }
  try {
    const data = JSON.parse(trimmed) as { detail?: unknown };
    if (typeof data.detail === "string") {
      return data.detail;
    }
    if (Array.isArray(data.detail) && data.detail.length > 0) {
      const first = data.detail[0] as { msg?: string };
      if (typeof first.msg === "string") {
        return first.msg;
      }
    }
  } catch {
    // ignore
  }
  return trimmed || `request failed: ${response.status}`;
}

export async function adminLogin(username: string, password: string): Promise<void> {
  const response = await fetch(`${API_BASE}/admin/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
  const data = await parseResponseJson<{ token: string }>(response);
  setAdminToken(data.token);
}

export async function adminLogout(): Promise<void> {
  const token = getAdminToken();
  if (token) {
    await fetch(`${API_BASE}/admin/logout`, {
      method: "POST",
      headers: authHeaders(),
    }).catch(() => undefined);
  }
  setAdminToken(null);
}

export async function adminMe(): Promise<{ username: string }> {
  const response = await fetch(`${API_BASE}/admin/me`, {
    headers: authHeaders(),
  });
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
  return parseResponseJson<{ username: string }>(response);
}

export type GeneratedKey = {
  key: string;
  tier: number;
  credits: number;
};

export async function adminGenerateKeys(input: {
  tier: number;
  count: number;
  note: string;
}): Promise<GeneratedKey[]> {
  const response = await fetch(`${API_BASE}/admin/keys/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
    body: JSON.stringify(input),
  });
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
  const data = await parseResponseJson<{ keys: GeneratedKey[] }>(response);
  return data.keys;
}

export type LicenseKeyRecord = {
  id: number;
  credits: number;
  tierLabel: string;
  status: string;
  note: string | null;
  createdAt: number;
  redeemedDeviceId: string | null;
  redeemedAt: number | null;
};

export async function adminListKeys(input?: {
  limit?: number;
  offset?: number;
  status?: "unused" | "redeemed";
}): Promise<{ items: LicenseKeyRecord[]; total: number }> {
  const params = new URLSearchParams();
  if (input?.limit != null) {
    params.set("limit", String(input.limit));
  }
  if (input?.offset != null) {
    params.set("offset", String(input.offset));
  }
  if (input?.status) {
    params.set("status", input.status);
  }
  const query = params.toString();
  const response = await fetch(`${API_BASE}/admin/keys${query ? `?${query}` : ""}`, {
    headers: authHeaders(),
  });
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
  return parseResponseJson<{ items: LicenseKeyRecord[]; total: number }>(response);
}
