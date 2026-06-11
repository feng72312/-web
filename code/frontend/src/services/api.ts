import type {
  InterpretResponse,
  LiuriDay,
  PaipanRequest,
  PaipanResponse,
} from "../types/bazi";
import type { InterpretStyle } from "../utils/interpretStyle";
import { API_BASE } from "./config";
import { jsonDeviceHeaders, jsonPublicHeaders, parseQuotaError } from "./deviceHeaders";
import { fetchWithTimeout, parseResponseJson } from "./httpJson";
import { refreshQuotaBar } from "../utils/quotaEvents";

async function postJson<T>(
  path: string,
  body: unknown,
  options?: { modelId?: string; auth?: boolean },
): Promise<T> {
  const headers =
    options?.auth === false
      ? jsonPublicHeaders()
      : await jsonDeviceHeaders(options?.modelId);
  const response = await fetchWithTimeout(`${API_BASE}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(parseQuotaError(text, response.status) || `Request failed: ${response.status}`);
  }
  return parseResponseJson<T>(response);
}

export function fetchPaipan(body: PaipanRequest): Promise<PaipanResponse> {
  return postJson<PaipanResponse>("/paipan", body, { auth: false });
}

export function fetchLuckTimeline(
  body: PaipanRequest,
): Promise<{ luckTimeline: NonNullable<PaipanResponse["chart"]["luckTimeline"]> }> {
  return postJson("/paipan/luck-timeline", body, { auth: false });
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
    fusionMode?: "bazi_liuyao" | "bazi_ziwei" | "triple";
    fusion?: boolean;
  },
): Promise<InterpretResponse> {
  const useFusion = options?.fusion === true && Boolean(options?.fusionMode);
  const payload = {
    ...body,
    fusion: useFusion,
    ...(useFusion ? { fusionMode: options?.fusionMode } : {}),
    ...(options?.excerpts ? { excerpts: options.excerpts } : {}),
    ...(options?.question ? { question: options.question } : {}),
    ...(options?.model ? { model: options.model } : {}),
    ...(options?.style ? { style: options.style } : {}),
  };
  const result = await postJson<InterpretResponse>("/interpret", payload, {
    modelId: options?.model,
  });
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
