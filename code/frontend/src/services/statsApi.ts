import { API_BASE } from "./config";
import { fetchWithTimeout } from "./httpJson";
import { getVisitorId } from "../utils/visitorId";

const STATS_BASE = `${API_BASE}/stats`;

export interface StatsOverview {
  online: number;
  total: number;
  visits: number;
}

export async function fetchStatsOverview(): Promise<StatsOverview> {
  const response = await fetchWithTimeout(`${STATS_BASE}/overview`, undefined, 8000);
  if (!response.ok) {
    throw new Error(`stats overview failed: ${response.status}`);
  }
  return response.json() as Promise<StatsOverview>;
}

export async function sendStatsHeartbeat(countVisit = false): Promise<StatsOverview> {
  const response = await fetchWithTimeout(
    `${STATS_BASE}/heartbeat`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ visitorId: getVisitorId(), countVisit }),
    },
    8000,
  );
  if (!response.ok) {
    throw new Error(`stats heartbeat failed: ${response.status}`);
  }
  return response.json() as Promise<StatsOverview>;
}
