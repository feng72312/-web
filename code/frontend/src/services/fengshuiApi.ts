import type {
  FengshuiChart,
  FengshuiChartRequest,
  FengshuiInterpretation,
  FengshuiMountain,
} from "../types/fengshui";
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
  const response = await fetch(`${API_BASE}${path}`, {
    headers: await jsonDeviceHeaders(),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function fetchFengshuiMountains(): Promise<{ mountains: FengshuiMountain[] }> {
  return getJson("/fengshui/mountains");
}

export function fetchFengshuiChart(
  body: FengshuiChartRequest,
): Promise<{ chart: FengshuiChart }> {
  return postJson("/fengshui/chart", body);
}

export function fetchFengshuiRagSearch(
  chart: FengshuiChart,
  question?: string,
): Promise<{ query: string; excerpts: FengshuiInterpretation["excerpts"] }> {
  return postJson("/fengshui/rag/search", { chart, question });
}

export async function fetchFengshuiInterpret(
  chart: FengshuiChart,
  excerpts?: FengshuiInterpretation["excerpts"],
  model?: string,
  style?: InterpretStyle,
): Promise<{ chart: FengshuiChart; interpretation: FengshuiInterpretation }> {
  const result = await postJson<{ chart: FengshuiChart; interpretation: FengshuiInterpretation }>(
    "/fengshui/interpret",
    { chart, excerpts, model, style },
    model,
  );
  refreshQuotaBar();
  return result;
}

export function initFengshuiChatSession(
  chart: FengshuiChart,
  excerpts?: FengshuiInterpretation["excerpts"],
  knowledgeHits?: FengshuiInterpretation["knowledgeHits"],
): Promise<{ agentId: string }> {
  return postJson("/fengshui/chat/init", { chart, excerpts, knowledgeHits });
}
