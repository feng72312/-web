import type {
  InterpretResponse,
  LiuriDay,
  PaipanRequest,
  PaipanResponse,
} from "../types/bazi";

const API_BASE = "/api/v1";

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function fetchPaipan(body: PaipanRequest): Promise<PaipanResponse> {
  return postJson<PaipanResponse>("/paipan", body);
}

export function fetchInterpret(body: PaipanRequest): Promise<InterpretResponse> {
  return postJson<InterpretResponse>("/interpret", body);
}

export async function fetchLiuri(
  year: number,
  dayMaster: string,
): Promise<{ year: number; months: Record<string, LiuriDay[]> }> {
  const response = await fetch(
    `${API_BASE}/liuri/${year}?dayMaster=${encodeURIComponent(dayMaster)}`,
  );
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}
