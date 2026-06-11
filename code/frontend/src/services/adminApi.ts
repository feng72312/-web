import { API_BASE } from "./config";
import { parseResponseJson } from "./httpJson";

const TOKEN_KEY = "bazi_admin_token_v1";

export class AdminAuthError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "AdminAuthError";
  }
}

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

async function adminFetch(input: string, init?: RequestInit): Promise<Response> {
  const response = await fetch(input, init);
  if (response.status === 401) {
    setAdminToken(null);
    throw new AdminAuthError("登录已过期, 请重新登录");
  }
  return response;
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
  const response = await adminFetch(`${API_BASE}/admin/me`, {
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
  const response = await adminFetch(`${API_BASE}/admin/keys/generate`, {
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

export type AdminLicenseSummary = {
  totalKeys: number;
  unusedKeys: number;
  redeemedKeys: number;
  totalCreditsIssued: number;
  totalCreditsRedeemed: number;
  latestCreatedAt: number | null;
  latestRedeemedAt: number | null;
};

export type AdminUsageStatsSummary = {
  online: number;
  totalVisitors: number;
  visits: number;
};

export type AdminPersistenceSummary = {
  likelyPersistent: boolean;
  warning: string | null;
  quotaDbPath: string;
  statsDbPath: string;
};

export type AdminOverview = {
  licenseSummary: AdminLicenseSummary;
  usageStats: AdminUsageStatsSummary;
  persistence: AdminPersistenceSummary;
};

export async function adminOverview(): Promise<AdminOverview> {
  const response = await adminFetch(`${API_BASE}/admin/overview`, {
    headers: authHeaders(),
  });
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
  return parseResponseJson<AdminOverview>(response);
}

export type AdminListKeysInput = {
  limit?: number;
  offset?: number;
  status?: "unused" | "redeemed";
  tier?: number;
  note?: string;
  redeemedDeviceId?: string;
  createdFrom?: number;
  createdTo?: number;
};

export async function adminListKeys(
  input?: AdminListKeysInput,
): Promise<{ items: LicenseKeyRecord[]; total: number }> {
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
  if (input?.tier != null) {
    params.set("tier", String(input.tier));
  }
  if (input?.note) {
    params.set("note", input.note);
  }
  if (input?.redeemedDeviceId) {
    params.set("redeemedDeviceId", input.redeemedDeviceId);
  }
  if (input?.createdFrom != null) {
    params.set("createdFrom", String(input.createdFrom));
  }
  if (input?.createdTo != null) {
    params.set("createdTo", String(input.createdTo));
  }
  const query = params.toString();
  const response = await adminFetch(`${API_BASE}/admin/keys${query ? `?${query}` : ""}`, {
    headers: authHeaders(),
  });
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
  return parseResponseJson<{ items: LicenseKeyRecord[]; total: number }>(response);
}
