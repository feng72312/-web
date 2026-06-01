import type {
  InterpretResponse,
  LiuriDay,
  PaipanRequest,
  PaipanResponse,
} from "../types/bazi";
import type { InterpretStyle } from "../utils/interpretStyle";
import { API_BASE } from "./config";
import { jsonDeviceHeaders, parseQuotaError } from "./deviceHeaders";
import { parseResponseJson } from "./httpJson";
import { refreshQuotaBar } from "../utils/quotaEvents";

async function postJson<T>(path: string, body: unknown, modelId?: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: jsonDeviceHeaders(modelId),
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(parseQuotaError(text, response.status) || `Request failed: ${response.status}`);
  }
  return parseResponseJson<T>(response);
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

export async function fetchInterpret(
  body: PaipanRequest,
  options?: {
    excerpts?: InterpretResponse["interpretation"]["excerpts"];
    question?: string;
    model?: string;
    style?: InterpretStyle;
  },
): Promise<InterpretResponse> {
  const payload = {
    ...body,
    ...(options?.excerpts ? { excerpts: options.excerpts } : {}),
    ...(options?.question ? { question: options.question } : {}),
    ...(options?.model ? { model: options.model } : {}),
    ...(options?.style ? { style: options.style } : {}),
  };
  const result = await postJson<InterpretResponse>("/interpret", payload, options?.model);
  refreshQuotaBar();
  return result;
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
