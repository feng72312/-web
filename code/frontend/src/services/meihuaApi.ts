import type {
  MeihuaChart,
  MeihuaDivineRequest,
  MeihuaInterpretation,
} from "../types/meihua";
import { API_BASE } from "./config";
import { jsonDeviceHeaders, parseQuotaError } from "./deviceHeaders";
import type { InterpretStyle } from "../utils/interpretStyle";
import { refreshQuotaBar } from "../utils/quotaEvents";

async function postJson<T>(path: string, body: unknown, modelId?: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: jsonDeviceHeaders(modelId),
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

export function fetchMeihuaDivine(
  body: MeihuaDivineRequest,
): Promise<{ chart: MeihuaChart }> {
  return postJson("/meihua/divine", body);
}

export function fetchMeihuaTiYong(
  chart: MeihuaChart,
  movingPosition: number,
): Promise<{ chart: MeihuaChart }> {
  return postJson("/meihua/ti-yong", { chart, movingPosition });
}

export function fetchMeihuaRagSearch(
  chart: MeihuaChart,
  question?: string,
): Promise<{ query: string; excerpts: MeihuaInterpretation["excerpts"] }> {
  return postJson("/meihua/rag/search", { chart, question });
}

export async function fetchMeihuaInterpret(
  chart: MeihuaChart,
  excerpts?: MeihuaInterpretation["excerpts"],
  model?: string,
  style?: InterpretStyle,
): Promise<{ chart: MeihuaChart; interpretation: MeihuaInterpretation }> {
  const result = await postJson<{ chart: MeihuaChart; interpretation: MeihuaInterpretation }>(
    "/meihua/interpret",
    { chart, excerpts, model, style },
    model,
  );
  refreshQuotaBar();
  return result;
}

export function initMeihuaChatSession(
  chart: MeihuaChart,
  excerpts?: MeihuaInterpretation["excerpts"],
  knowledgeHits?: MeihuaInterpretation["knowledgeHits"],
): Promise<{ agentId: string }> {
  return postJson("/meihua/chat/init", { chart, excerpts, knowledgeHits });
}
