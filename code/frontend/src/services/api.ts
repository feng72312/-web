import type {
  InterpretResponse,
  LiuriDay,
  PaipanRequest,
  PaipanResponse,
} from "../types/bazi";
import { API_BASE } from "./config";

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

export function fetchLuckTimeline(
  body: PaipanRequest,
): Promise<{ luckTimeline: NonNullable<PaipanResponse["chart"]["luckTimeline"]> }> {
  return postJson("/paipan/luck-timeline", body);
}

export interface RagSearchResult {
  query: string;
  excerpts: InterpretResponse["interpretation"]["excerpts"];
}

export function fetchRagSearch(body: PaipanRequest): Promise<RagSearchResult> {
  return postJson<RagSearchResult>("/rag/search", body);
}

export function fetchInterpret(
  body: PaipanRequest,
  excerpts?: InterpretResponse["interpretation"]["excerpts"],
): Promise<InterpretResponse> {
  const payload = excerpts ? { ...body, excerpts } : body;
  return postJson<InterpretResponse>("/interpret", payload);
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
