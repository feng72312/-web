import type { PaipanRequest, PaipanResponse } from "../types/bazi";
import type { BirthProfileSummary } from "../types/qimen";

const STORAGE_KEY = "bazi_last_chart_v1";

export function saveBaziChartRef(
  paipan: PaipanResponse,
  request: PaipanRequest,
): void {
  const p = paipan.chart.pillars;
  const payload: BirthProfileSummary = {
    year: p.year.ganzhi,
    month: p.month.ganzhi,
    day: p.day.ganzhi,
    hour: p.hour.ganzhi,
    gender: request.gender === 1 ? "男" : "女",
    summary: `命主 ${request.name.trim() || "未命名"}`,
  };
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  } catch {
    /* ignore quota */
  }
}

export function loadBaziBirthProfile(): BirthProfileSummary | null {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as BirthProfileSummary;
  } catch {
    return null;
  }
}

export function clearBaziChartRef(): void {
  sessionStorage.removeItem(STORAGE_KEY);
}
