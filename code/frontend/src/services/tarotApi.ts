import type {
  SpreadDef,
  TarotDeckInfo,
  TarotDrawRequest,
  TarotInterpretation,
  TarotReading,
} from "../types/tarot";
import { API_BASE } from "./config";
import { jsonDeviceHeaders, parseQuotaError } from "./deviceHeaders";
import type { InterpretStyle } from "../utils/interpretStyle";
import { refreshQuotaBar } from "../utils/quotaEvents";

async function postJson<T>(path: string, body: unknown, modelId?: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: await jsonDeviceHeaders(modelId),
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const text = await response.text();
    if (response.status === 402) {
      refreshQuotaBar();
    }
    throw new Error(parseQuotaError(text, response.status) || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function fetchTarotDecks(): Promise<{ decks: TarotDeckInfo[] }> {
  return getJson("/tarot/decks");
}

export function fetchTarotSpreads(): Promise<{ spreads: SpreadDef[] }> {
  return getJson("/tarot/spreads");
}

export function suggestTarotSpread(
  question: string,
): Promise<{ spreadId: string; reason: string }> {
  return postJson("/tarot/suggest-spread", { question });
}

export function drawTarot(body: TarotDrawRequest): Promise<{ reading: TarotReading }> {
  return postJson("/tarot/draw", body);
}

export function fetchTarotRagSearch(
  reading: TarotReading,
  question?: string,
): Promise<{ query: string; excerpts: TarotInterpretation["excerpts"] }> {
  return postJson("/tarot/rag/search", { reading, question });
}

export async function fetchTarotInterpret(
  reading: TarotReading,
  excerpts?: TarotInterpretation["excerpts"],
  model?: string,
  style?: InterpretStyle,
): Promise<{ reading: TarotReading; interpretation: TarotInterpretation }> {
  const result = await postJson<{ reading: TarotReading; interpretation: TarotInterpretation }>(
    "/tarot/interpret",
    {
      reading,
      excerpts,
      model,
      style,
    },
    model,
  );
  refreshQuotaBar();
  return result;
}

export function initTarotChatSession(
  reading: TarotReading,
  excerpts?: TarotInterpretation["excerpts"],
): Promise<{ agentId: string }> {
  return postJson("/tarot/chat/init", { reading, excerpts });
}
