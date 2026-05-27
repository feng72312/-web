import { API_BASE } from "./config";
import { getVisitorId } from "../utils/visitorId";

const STATS_BASE = `${API_BASE}/stats`;

export interface StatsOverview {
  online: number;
  total: number;
}

export async function fetchStatsOverview(): Promise<StatsOverview> {
  const response = await fetch(`${STATS_BASE}/overview`);
  if (!response.ok) {
    throw new Error(`stats overview failed: ${response.status}`);
  }
  return response.json() as Promise<StatsOverview>;
}

export async function sendStatsHeartbeat(): Promise<StatsOverview> {
  const response = await fetch(`${STATS_BASE}/heartbeat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ visitorId: getVisitorId() }),
  });
  if (!response.ok) {
    throw new Error(`stats heartbeat failed: ${response.status}`);
  }
  return response.json() as Promise<StatsOverview>;
}
