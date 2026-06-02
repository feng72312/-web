import { API_BASE } from "./config";
import { getAccessToken } from "./cloudbaseClient";
import { getVisitorId } from "../utils/visitorId";

export async function authApiHeaders(): Promise<Record<string, string>> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "X-Device-Id": getVisitorId(),
  };
  const token = await getAccessToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

export async function mergeDeviceQuota(): Promise<void> {
  const token = await getAccessToken();
  if (!token) {
    return;
  }
  const response = await fetch(`${API_BASE}/auth/merge-device`, {
    method: "POST",
    headers: await authApiHeaders(),
    body: JSON.stringify({ deviceId: getVisitorId() }),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `merge failed: ${response.status}`);
  }
}
