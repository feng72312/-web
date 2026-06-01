import { API_BASE } from "./config";
import { getVisitorId } from "../utils/visitorId";

export interface TierQuota {
  tier: string;
  remaining: number;
  limit: number;
}

export interface QuotaStatus {
  deviceId: string;
  phone: string | null;
  freeRemaining: number;
  freeDailyLimit: number;
  creditBalance: number;
  tierQuotas?: TierQuota[];
}

export interface QuotaPersistence {
  likelyPersistent: boolean;
  warning: string | null;
}

export async function fetchQuotaPersistence(): Promise<QuotaPersistence | null> {
  try {
    const response = await fetch(`${API_BASE}/quota/persistence`);
    if (!response.ok) {
      return null;
    }
    const data = (await response.json()) as QuotaPersistence;
    return data;
  } catch {
    return null;
  }
}

export async function fetchQuotaStatus(): Promise<QuotaStatus> {
  const deviceId = getVisitorId();
  const response = await fetch(
    `${API_BASE}/quota/status?deviceId=${encodeURIComponent(deviceId)}`,
  );
  if (!response.ok) {
    throw new Error(`quota status failed: ${response.status}`);
  }
  return response.json() as Promise<QuotaStatus>;
}

export async function redeemLicenseKey(key: string): Promise<{
  addedCredits: number;
  creditBalance: number;
}> {
  const response = await fetch(`${API_BASE}/quota/redeem`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ deviceId: getVisitorId(), key: key.trim() }),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `redeem failed: ${response.status}`);
  }
  return response.json() as Promise<{ addedCredits: number; creditBalance: number }>;
}

export async function bindQuotaPhone(phone: string): Promise<void> {
  const response = await fetch(`${API_BASE}/quota/bind-phone`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ deviceId: getVisitorId(), phone: phone.trim() }),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `bind phone failed: ${response.status}`);
  }
}
